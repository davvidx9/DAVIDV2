"""
Asterisk ARI call control (replaces Telnyx Call Control SDK).

Handles originate, playback (TTS files), DTMF, recording, hangup, and Stasis events.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional
from urllib.parse import quote

import requests
from websocket import WebSocketApp

from config import (
    ARI_APP,
    ARI_PASSWORD,
    ARI_URL,
    ARI_USERNAME,
    CALL_TIMEOUT_SEC,
    CALLER_ID_NAME,
    CALLER_ID_NUMBER,
    SIP_ENDPOINT,
)

logger = logging.getLogger(__name__)


@dataclass
class CallContext:
    """Per-call state (stored when originating)."""

    channel_id: str
    route: str
    chat_id: int
    tag: str
    callee: str
    meta: Dict[str, str] = field(default_factory=dict)
    digits_buffer: str = ""
    gather_max: int = 1
    gather_prompt: str = ""
    gather_language: str = "en"
    step: str = "init"
    recording_name: Optional[str] = None


class AriCallManager:
    """Sync ARI REST + WebSocket event loop."""

    def __init__(self, on_event: Callable[[str, CallContext, dict], None]):
        self._auth = (ARI_USERNAME, ARI_PASSWORD)
        self._base = ARI_URL.rstrip("/")
        self._on_event = on_event
        self._calls: Dict[str, CallContext] = {}
        self._ws: Optional[WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        ws_url = (
            self._base.replace("http://", "ws://").replace("https://", "wss://")
            + f"/events?api_key={quote(ARI_USERNAME)}:{quote(ARI_PASSWORD)}"
            + f"&app={ARI_APP}&subscribeAll=true"
        )

        def on_message(_ws, message: str):
            import json

            try:
                self._handle_ari_event(json.loads(message))
            except Exception:
                logger.exception("ARI event error")

        self._ws = WebSocketApp(ws_url, on_message=on_message)
        self._thread = threading.Thread(target=self._ws.run_forever, daemon=True)
        self._thread.start()
        logger.info("ARI WebSocket started app=%s", ARI_APP)

    def _req(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{self._base}/{path.lstrip('/')}"
        r = requests.request(method, url, auth=self._auth, timeout=30, **kwargs)
        r.raise_for_status()
        return r

    def originate(
        self,
        to_number: str,
        route: str,
        chat_id: int,
        tag: str,
        meta: Optional[Dict[str, str]] = None,
        record: bool = False,
    ) -> CallContext:
        """Outbound call via PJSIP trunk; caller ID = client number from env."""
        digits = "".join(c for c in to_number if c.isdigit())
        endpoint = f"PJSIP/{digits}@{SIP_ENDPOINT}"
        variables = {
            "IVR_ROUTE": route,
            "IVR_CHAT_ID": str(chat_id),
            "IVR_TAG": tag or "",
            "IVR_RECORD": "1" if record else "0",
        }
        if meta:
            for k, v in meta.items():
                variables[f"IVR_META_{k.upper()}"] = str(v)

        caller_id = CALLER_ID_NUMBER
        if caller_id and not caller_id.startswith("+"):
            caller_id = f"+{caller_id}"

        params: Dict[str, Any] = {
            "endpoint": endpoint,
            "app": ARI_APP,
            "appArgs": route,
            "callerId": (
                f'"{CALLER_ID_NAME}" <{caller_id}>' if caller_id else CALLER_ID_NAME
            ),
        }
        for k, v in variables.items():
            params[f"variables[{k}]"] = v

        data = self._req("POST", "channels", params=params).json()
        ch_id = data["id"]
        ctx = CallContext(
            channel_id=ch_id,
            route=route,
            chat_id=chat_id,
            tag=tag,
            callee=digits,
            meta=meta or {},
        )
        self._calls[ch_id] = ctx
        threading.Timer(CALL_TIMEOUT_SEC, self._timeout_hangup, args=[ch_id]).start()
        return ctx

    def _timeout_hangup(self, channel_id: str) -> None:
        ctx = self._calls.get(channel_id)
        if ctx and ctx.step not in ("ended",):
            try:
                self.hangup(channel_id)
            except Exception:
                pass

    def hangup(self, channel_id: str) -> None:
        try:
            self._req("DELETE", f"channels/{channel_id}")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return
            raise
        ctx = self._calls.get(channel_id)
        if ctx:
            ctx.step = "ended"

    def play_sound(self, channel_id: str, sound_uri: str) -> str:
        """Play media; sound_uri e.g. sound:hello or sound:custom/foo."""
        r = self._req(
            "POST",
            f"channels/{channel_id}/play",
            params={"media": sound_uri},
        ).json()
        return r["id"]

    def speak_tts_file(self, channel_id: str, asterisk_sound: str) -> str:
        """Play file already in Asterisk sounds dir (no extension)."""
        return self.play_sound(channel_id, f"sound:{asterisk_sound}")

    def start_recording(self, channel_id: str, name: str) -> None:
        ctx = self._calls.get(channel_id)
        if ctx:
            ctx.recording_name = name
        self._req(
            "POST",
            f"channels/{channel_id}/record",
            params={
                "name": name,
                "format": "wav",
                "maxDurationSeconds": CALL_TIMEOUT_SEC,
                "beep": "false",
                "ifExists": "overwrite",
            },
        )

    def gather_dtmf(
        self,
        channel_id: str,
        prompt_sound: str,
        max_digits: int,
        timeout_ms: int = 15000,
    ) -> None:
        ctx = self._calls.get(channel_id)
        if not ctx:
            return
        ctx.gather_max = max_digits
        ctx.digits_buffer = ""
        ctx.step = "gathering"
        self.speak_tts_file(channel_id, prompt_sound)

    def _handle_ari_event(self, event: dict) -> None:
        etype = event.get("type")
        ch = event.get("channel") or {}
        ch_id = ch.get("id")
        if not ch_id:
            return

        if etype == "StasisStart":
            ctx = self._calls.get(ch_id)
            if not ctx:
                vars_map = ch.get("channelvars") or {}
                ctx = CallContext(
                    channel_id=ch_id,
                    route=vars_map.get("IVR_ROUTE", "voice"),
                    chat_id=int(vars_map.get("IVR_CHAT_ID", "0") or 0),
                    tag=vars_map.get("IVR_TAG", ""),
                    callee=ch.get("caller", {}).get("number", ""),
                    meta={},
                )
                for k, v in vars_map.items():
                    if k.startswith("IVR_META_"):
                        ctx.meta[k.replace("IVR_META_", "").lower()] = v
                self._calls[ch_id] = ctx
            self._on_event("call.answered", ctx, event)
            return

        ctx = self._calls.get(ch_id)
        if not ctx:
            return

        if etype == "ChannelDtmfReceived":
            digit = event.get("digit", "")
            if ctx.step == "gathering":
                ctx.digits_buffer += digit
                if len(ctx.digits_buffer) >= ctx.gather_max:
                    self._on_event(
                        "call.gather.ended", ctx, {"digits": ctx.digits_buffer}
                    )
            else:
                self._on_event("call.dtmf", ctx, {"digit": digit, "digits": digit})
            return

        if etype == "PlaybackFinished":
            if ctx.step == "gathering" and not ctx.digits_buffer:
                self._on_event("playback.finished", ctx, event)
            return

        if etype == "RecordingFinished":
            rec = event.get("recording", {})
            self._on_event("call.recording.saved", ctx, rec)
            return

        if etype == "StasisEnd":
            ctx.step = "ended"
            self._on_event("call.hangup", ctx, event)
            self._calls.pop(ch_id, None)


# Global instance set by api.py
manager: Optional[AriCallManager] = None

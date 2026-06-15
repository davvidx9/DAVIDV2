#!/usr/bin/env python3
"""Telegram bot — /chk with single persistent browser tab."""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from fill_payment_form import get_persistent_session


ROOT = Path(__file__).resolve().parent
BOT_CONFIG_PATH = ROOT / "bot_config.json"
BOT_CONFIG_EXAMPLE = ROOT / "bot_config.json.example"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s", force=True)
logger = logging.getLogger("telegram_bot")
logger.propagate = False
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(_handler)


def load_bot_config() -> dict:
    path = BOT_CONFIG_PATH if BOT_CONFIG_PATH.exists() else BOT_CONFIG_EXAMPLE
    if not path.exists():
        raise FileNotFoundError("bot_config.json not found — copy bot_config.json.example")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_chk_message(text: str) -> dict[str, str] | None:
    card = month = year = cvc = None
    patterns = {
        "card": re.compile(r"card\s*:\s*(\d[\d\s]{12,18}\d)", re.I),
        "month": re.compile(r"month\s*:\s*(\d{1,2})", re.I),
        "year": re.compile(r"year\s*:\s*(\d{2,4})", re.I),
        "cvc": re.compile(r"cvc2?\s*:\s*(\d{3,4})", re.I),
    }

    for line in text.splitlines():
        line = line.strip()
        if line.startswith("/chk"):
            line = line[4:].strip()
        for key, pattern in patterns.items():
            match = pattern.search(line)
            if match:
                value = match.group(1).strip()
                if key == "card":
                    card = value.replace(" ", "")
                elif key == "month":
                    month = value
                elif key == "year":
                    year = value
                elif key == "cvc":
                    cvc = value

    if card and month and year and cvc:
        return {"card": card, "month": month, "year": year, "cvc": cvc}
    return None


def mask_card(card: str) -> str:
    digits = card.replace(" ", "")
    if len(digits) < 8:
        return "****"
    return f"{digits[:4]}****{digits[-4:]}"


async def process_card_check(card: str, month: str, year: str, cvc: str) -> dict:
    session = get_persistent_session()
    return await session.run_card(card, month, year, cvc)


async def reply_result(update: Update, result: dict, card_masked: str) -> None:
    reused = " (nfs tab)" if result.get("reused_tab") else " (tab jdid)"
    if result.get("card_added"):
        text = f"✅ Done{reused}\n\n💳 {card_masked}\n📝 {result.get('message', 'OK')}"
    else:
        text = f"❌ Failed{reused}\n\n💳 {card_masked}\n📝 {result.get('message', 'Error')}"

    screenshot = result.get("screenshot")
    if screenshot and Path(screenshot).exists():
        with Path(screenshot).open("rb") as handle:
            await update.effective_message.reply_photo(handle, caption=text)
    else:
        await update.effective_message.reply_text(text)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salam! Browser kaybqa f tab wa7da.\n\n"
        "/chk card: 5294153155207609\n"
        "month: 4\n"
        "year: 2027\n"
        "cvc2: 896\n\n"
        "Lmarra l-ula: login + payment page\n"
        "Lmarra jaya: redirect nfs tab bla ma ytf7 jdid\n\n"
        "Billing dima:\n"
        "• david alaba\n"
        "• New York\n"
        "• postal: 10080"
    )


async def cmd_chk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if context.args:
        text = "/chk " + " ".join(context.args) + "\n" + text

    parsed = parse_chk_message(text)
    if not parsed:
        await update.message.reply_text(
            "❌ Format ghalat:\n\n"
            "/chk card: 5294153155207609\n"
            "month: 4\n"
            "year: 2027\n"
            "cvc2: 896"
        )
        return

    card_masked = mask_card(parsed["card"])
    await update.message.reply_text(f"⏳ Processing {card_masked}...")

    try:
        result = await process_card_check(parsed["card"], parsed["month"], parsed["year"], parsed["cvc"])
        await reply_result(update, result, card_masked)
    except Exception as exc:
        logger.exception("Processing failed")
        await update.message.reply_text(f"❌ Error: {exc}")


async def on_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    lower = text.lower()
    if "/chk" in lower or ("card:" in lower and "month:" in lower):
        await cmd_chk(update, context)


def main() -> None:
    config = load_bot_config()
    token = config.get("telegram_bot_token", "").strip()
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        raise SystemExit("3mer telegram_bot_token f bot_config.json (mn @BotFather)")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("chk", cmd_chk))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_message))

    logger.info("Telegram bot running — single tab mode")
    app.run_polling()


if __name__ == "__main__":
    main()

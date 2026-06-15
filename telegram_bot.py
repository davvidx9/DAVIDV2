#!/usr/bin/env python3
"""Telegram bot — /chk card checker for SignalWire."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from fill_payment_form import run_automation


ROOT = Path(__file__).resolve().parent
BOT_CONFIG_PATH = ROOT / "bot_config.json"
BOT_CONFIG_EXAMPLE = ROOT / "bot_config.json.example"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("telegram_bot")


def load_bot_config() -> dict:
    path = BOT_CONFIG_PATH if BOT_CONFIG_PATH.exists() else BOT_CONFIG_EXAMPLE
    if not path.exists():
        raise FileNotFoundError("bot_config.json not found — copy bot_config.json.example")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def parse_chk_message(text: str) -> dict[str, str] | None:
    """Parse:
    /chk card: 5294153155207609
    month: 4
    year: 2027
    cvc2: 896
    """
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
    return await run_automation(
        card_number=card,
        month=month,
        year=year,
        cvc=cvc,
        interactive=False,
        submit_card=True,
    )


async def reply_result(update: Update, result: dict, card_masked: str) -> None:
    if result.get("card_added"):
        text = f"✅ Card ADDED\n\n💳 {card_masked}\n📝 {result.get('message', 'Success')}"
    elif result.get("success"):
        text = f"✅ Done\n\n💳 {card_masked}\n📝 {result.get('message', 'OK')}"
    else:
        text = f"❌ Card NOT added\n\n💳 {card_masked}\n📝 {result.get('message', 'Failed')}"

    screenshot = result.get("screenshot")
    if screenshot and Path(screenshot).exists():
        with Path(screenshot).open("rb") as handle:
            await update.effective_message.reply_photo(handle, caption=text)
    else:
        await update.effective_message.reply_text(text)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Salam! Sift commande b had format:\n\n"
        "/chk card: 5294153155207609\n"
        "month: 4\n"
        "year: 2027\n"
        "cvc2: 896\n\n"
        "Billing info dima:\n"
        "• name: david alaba\n"
        "• address: New York\n"
        "• city: New York\n"
        "• country: United States"
    )


async def cmd_chk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    if context.args:
        text = "/chk " + " ".join(context.args) + "\n" + text

    parsed = parse_chk_message(text)
    if not parsed:
        await update.message.reply_text(
            "❌ Format ghalat. Sift haka:\n\n"
            "/chk card: 5294153155207609\n"
            "month: 4\n"
            "year: 2027\n"
            "cvc2: 896"
        )
        return

    card_masked = mask_card(parsed["card"])
    await update.message.reply_text(f"⏳ Kanchecki card {card_masked}...")

    try:
        result = await process_card_check(parsed["card"], parsed["month"], parsed["year"], parsed["cvc"])
        await reply_result(update, result, card_masked)
    except Exception as exc:
        logger.exception("Card check failed")
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

    logger.info("Telegram bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()

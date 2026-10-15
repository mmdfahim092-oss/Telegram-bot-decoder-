"""Telegram bot for statically decoding common obfuscated HTML wrappers."""
from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from decoder import decode_html

BOT_TOKEN = os.environ.get("8835771700:AAFFTw6W6rp876QXgcpILYv-E1qU7gPAkQE", "").strip()
MAX_FILE_BYTES = 10 * 1024 * 1024  # 10 MB safety limit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("html-decoder-bot")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "HTML Decoder Bot-এ স্বাগতম। একটি .html/.htm ফাইল পাঠান, আমি পরিচিত "
        "Base64 JavaScript wrapper-গুলোকে শুধু টেক্সট হিসেবে ডিকোড করে ফেরত দেব।\n\n"
        "নিরাপত্তা: ডিকোড করা কোড কখনো চালানো হয় না। /help লিখে সাহায্য দেখুন।"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "ব্যবহার: একটি HTML ফাইল document হিসেবে পাঠান।\n"
        "সমর্থিত: index-ভিত্তিক Base64 chunk array এবং JavaScript-এ জোড়া লাগানো Base64 string।\n"
        "সীমা: সর্বোচ্চ 10 MB। অন্য ধরনের obfuscation হলে ফাইল অপরিবর্তিত ফেরত যেতে পারে।\n"
        "এটি HTML/JavaScript execute করে না, URL fetch করে না, বা remote content খোলে না।"
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.effective_message
    document = message.document if message else None
    if not document:
        return
    name = document.file_name or "uploaded.html"
    if Path(name).suffix.lower() not in {".html", ".htm"}:
        await message.reply_text("দয়া করে .html বা .htm ফাইল পাঠান।")
        return
    if document.file_size and document.file_size > MAX_FILE_BYTES:
        await message.reply_text("ফাইলটি 10 MB সীমার চেয়ে বড়।")
        return

    await message.chat.send_action(ChatAction.TYPING)
    tg_file = await context.bot.get_file(document.file_id)
    with tempfile.TemporaryDirectory(prefix="html-decoder-") as tmp:
        input_path = Path(tmp) / "input.html"
        await tg_file.download_to_drive(custom_path=str(input_path))
        if input_path.stat().st_size > MAX_FILE_BYTES:
            await message.reply_text("ফাইলটি 10 MB সীমার চেয়ে বড়।")
            return
        try:
            source = input_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            await message.reply_text("ফাইলটি UTF-8 টেক্সট হিসেবে পড়া যাচ্ছে না।")
            return

        result = decode_html(source)
        safe_name = Path(name).stem[:60] or "decoded"
        output_path = Path(tmp) / f"{safe_name}_decoded.html"
        output_path.write_text(result.text, encoding="utf-8")
        summary = "\n".join(result.notes)
        await message.reply_document(
            document=str(output_path),
            filename=output_path.name,
            caption=f"ডিকোড স্তর: {result.layers}\n{summary}\n\nকোড চালানো হয়নি।",
        )


async def unknown_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("একটি .html বা .htm ফাইল document হিসেবে পাঠান।")


def main() -> None:
    if not BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN environment variable সেট করুন।")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.ALL, unknown_file))
    log.info("HTML decoder bot started")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
  

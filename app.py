import os

from flask import Flask, request

import pdfplumber
import pandas as pd

from telegram import Bot, Update
from telegram.ext import Dispatcher, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN env var is not set")

bot = Bot(TOKEN)
app = Flask(__name__)

# Dispatcher (no update_queue because we use webhooks)
dispatcher = Dispatcher(bot, None, workers=0, use_context=True)


def start(update, context):
    update.message.reply_text("Send me a PDF and I’ll convert it to Excel 📊🔥")


def handle_pdf(update, context):
    message = update.message

    if not message.document:
        message.reply_text("Please upload a PDF file 😄")
        return

    document = message.document

    if not document.file_name.lower().endswith(".pdf"):
        message.reply_text("Please upload a PDF file 😄")
        return

    message.reply_text("Processing your file… Please wait ⏳")

    # Download file
    file = document.get_file()
    pdf_path = f"/tmp/{document.file_name}"
    excel_path = pdf_path.replace(".pdf", ".xlsx")

    file.download(pdf_path)

    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    all_rows.append(row)

    if not all_rows:
        message.reply_text("⚠️ Could not extract any table from this PDF!")
        return

    df = pd.DataFrame(all_rows)
    df.to_excel(excel_path, index=False)

    # Send back the Excel
    with open(excel_path, "rb") as f:
        message.reply_document(
            document=f,
            filename=os.path.basename(excel_path),
            caption="Here is your converted Excel file 😊",
        )


# Handlers
dispatcher.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
dispatcher.add_handler(MessageHandler(Filters.command, start))


@app.route("/")
def home():
    return "🚀 Telegram PDF Converter Bot Running!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True, silent=True)
    if json_update:
        update = Update.de_json(json_update, bot)
        dispatcher.process_update(update)
    return "ok", 200


if __name__ == "__main__":
    # Local development only; Render will use gunicorn
    app.run(host="0.0.0.0", port=10000, debug=True)

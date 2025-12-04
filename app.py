import os
import pdfplumber
import pandas as pd
from flask import Flask, request
from telegram import Bot
from telegram.ext import Dispatcher, MessageHandler, Filters

TOKEN = os.getenv("BOT_TOKEN")  # Set in Render environment variables
bot = Bot(TOKEN)

app = Flask(__name__)

# Telegram Dispatcher
dispatcher = Dispatcher(bot, None, workers=0)


# Start Command
def start(update, context):
    update.message.reply_text("Send me a PDF and I’ll convert it to Excel 📊🔥")


# Handle document uploads
def handle_pdf(update, context):
    document = update.message.document

    if not document.file_name.lower().endswith(".pdf"):
        update.message.reply_text("Please upload a PDF file 😄")
        return

    update.message.reply_text("Processing your file… Please wait ⏳")

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
        update.message.reply_text("⚠️ Could not extract any table from this PDF!")
        return

    df = pd.DataFrame(all_rows)
    df.to_excel(excel_path, index=False)

    update.message.reply_document(
        document=open(excel_path, "rb"),
        filename=os.path.basename(excel_path),
        caption="Here is your converted Excel file 😊"
    )


dispatcher.add_handler(MessageHandler(Filters.document.pdf, handle_pdf))
dispatcher.add_handler(MessageHandler(Filters.command, start))


@app.route("/")
def home():
    return "🚀 Telegram PDF Converter Bot Running!"


@app.route(f"/webhook/{TOKEN}", methods=["POST"])
def webhook():
    json_update = request.get_json(force=True, silent=True)
    if json_update:
        dispatcher.process_update(
            telegram.Update.de_json(json_update, bot)
        )
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

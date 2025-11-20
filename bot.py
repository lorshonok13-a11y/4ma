import json
import os
import logging
from dotenv import load_dotenv
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

logging.basicConfig(level=logging.INFO)

# Загружаем контент
with open("content.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

SECTIONS = CONTENT["sections"]
BUY_URL = CONTENT["buy_url"]
CONTACT_URL = CONTENT["contact_url"]
WELCOME_TEXT = CONTENT["welcome_text"]

# --- Клавиатуры ---
def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["Выбрать раздел"],
            ["Купить планер", "Связаться с автором"],
            ["Помощь"]
        ],
        resize_keyboard=True
    )

def sections_keyboard():
    buttons = []
    row = []
    for i, sec in enumerate(SECTIONS, 1):
        row.append(sec["title"])
        if i % 2 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append(["Назад"])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


# --- Хэндлеры ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_keyboard())

async def choose_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите раздел:", reply_markup=sections_keyboard())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(BUY_URL)

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(CONTACT_URL)

async def help_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите раздел — и я покажу пример заполнения.")

async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=main_keyboard())

async def show_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    section = next((s for s in SECTIONS if s["title"] == text), None)
    if not section:
        return

    if section["image"]:
        await update.message.reply_photo(section["image"], caption=section["text"])
    else:
        await update.message.reply_text(section["text"])


# --- Запуск ---
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text("Выбрать раздел"), choose_section))
    app.add_handler(MessageHandler(filters.Text("Купить планер"), buy))
    app.add_handler(MessageHandler(filters.Text("Связаться с автором"), contact))
    app.add_handler(MessageHandler(filters.Text("Помощь"), help_msg))
    app.add_handler(MessageHandler(filters.Text("Назад"), back))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_section))

    app.run_polling()

if __name__ == "__main__":
    main()

import os
import json
from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

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
def start(update, context):
    update.message.reply_text(WELCOME_TEXT, reply_markup=main_keyboard())

def choose_section(update, context):
    update.message.reply_text("Выберите раздел:", reply_markup=sections_keyboard())

def buy(update, context):
    update.message.reply_text(BUY_URL)

def contact(update, context):
    update.message.reply_text(CONTACT_URL)

def help_msg(update, context):
    update.message.reply_text("Выберите раздел — и я покажу пример заполнения.")

def back(update, context):
    update.message.reply_text("Главное меню:", reply_markup=main_keyboard())

def show_section(update, context):
    text = update.message.text
    section = next((s for s in SECTIONS if s["title"] == text), None)
    if not section:
        return
    
    # Если есть URL картинки, отправляем фото
    if section.get("image"):
        update.message.reply_photo(section["image"], caption=section["text"])
    else:
        update.message.reply_text(section["text"])

# --- Запуск ---
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text("Выбрать раздел"), choose_section))
dp.add_handler(MessageHandler(Filters.text("Купить планер"), buy))
dp.add_handler(MessageHandler(Filters.text("Связаться с автором"), contact))
dp.add_handler(MessageHandler(Filters.text("Помощь"), help_msg))
dp.add_handler(MessageHandler(Filters.text("Назад"), back))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, show_section))

updater.start_polling()
updater.idle()

import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Загружаем контент
with open("content.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = CONTENT["welcome_text"]
    keyboard = [[InlineKeyboardButton(s["title"], callback_data=s["id"])] for s in CONTENT["sections"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

# Обработка нажатий
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    section_id = query.data
    section = next((s for s in CONTENT["sections"] if s["id"] == section_id), None)
    if section:
        if section.get("image"):
            await query.message.reply_photo(section["image"], caption=section["text"])
        else:
            await query.message.reply_text(section["text"])

# Создаём приложение
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Запуск бота
app.run_polling()

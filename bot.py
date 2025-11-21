import json
import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Загружаем контент
with open("content.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

# Функция для создания клавиатуры с разделами
def get_keyboard():
    keyboard = [[InlineKeyboardButton(s["title"], callback_data=s["id"])] for s in CONTENT["sections"]]
    return InlineKeyboardMarkup(keyboard)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = CONTENT["welcome_text"]
    await update.message.reply_text(welcome_text, reply_markup=get_keyboard())

# Обработка нажатий кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    section_id = query.data
    section = next((s for s in CONTENT["sections"] if s["id"] == section_id), None)
    
    if section:
        images = section.get("images")
        if images:
            # Отправляем альбом
            media = [InputMediaPhoto(url) for url in images]
            media[0].caption = section["text"]  # текст на первой картинке
            await query.message.reply_media_group(media)
            
            # Отдельное сообщение с кнопками
            await query.message.reply_text(
                "Выберите раздел:",
                reply_markup=get_keyboard()
            )
        elif section.get("image"):
            await query.message.reply_photo(section["image"], caption=section["text"])
            await query.message.reply_text("Выберите раздел:", reply_markup=get_keyboard())
        else:
            await query.message.reply_text(section["text"], reply_markup=get_keyboard())

# Создаём приложение
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Запуск бота
app.run_polling()

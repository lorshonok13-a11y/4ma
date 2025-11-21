import json
import os
import asyncio
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
    await query.answer()  # подтверждаем callback

    section_id = query.data
    section = next((s for s in CONTENT["sections"] if s["id"] == section_id), None)

    if not section:
        return

    chat_id = query.message.chat_id
    images = section.get("images")

    if images:
        # формируем альбом
        media = [InputMediaPhoto(url) for url in images]
        media[0].caption = section["text"]

        # небольшая пауза перед отправкой альбома
        await asyncio.sleep(0.2)
        await context.bot.send_media_group(chat_id=chat_id, media=media)

    elif section.get("image"):
        await asyncio.sleep(0.1)
        await context.bot.send_photo(chat_id=chat_id, photo=section["image"], caption=section["text"])
    else:
        await asyncio.sleep(0.1)
        await context.bot.send_message(chat_id=chat_id, text=section["text"])

    # снова небольшая пауза перед отправкой меню
    await asyncio.sleep(0.2)
    await context.bot.send_message(chat_id=chat_id, text="Выберите раздел:", reply_markup=get_keyboard())

# Создаём приложение
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Запуск бота
app.run_polling()

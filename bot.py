import json
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем конфиг
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

WELCOME_TEXT = CONFIG["welcome_text"]
BUY_URL = CONFIG["buy_url"]
CONTACT_URL = CONFIG["contact_url"]
SECTIONS = CONFIG["sections"]

# Генерируем кнопки разделов
def get_sections_keyboard():
    keyboard = []
    for section in SECTIONS:
        keyboard.append([InlineKeyboardButton(section["title"], callback_data=section["id"])])
    return InlineKeyboardMarkup(keyboard)

# Главное меню (кнопки "Купить" и "Связаться")
def get_main_menu():
    keyboard = [
        [InlineKeyboardButton("Купить", url=BUY_URL)],
        [InlineKeyboardButton("Связаться", url=CONTACT_URL)],
        [InlineKeyboardButton("Выбрать раздел", callback_data="sections")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=get_main_menu())

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    section_id = query.data

    # Показать список разделов
    if section_id == "sections":
        await query.message.reply_text("Выберите раздел:", reply_markup=get_sections_keyboard())
        return

    # Найти раздел
    section = next((s for s in SECTIONS if s["id"] == section_id), None)

    if not section:
        await query.message.reply_text("Раздел не найден.")
        return

    image = section.get("image")
    text = section.get("text", "")

    # Отправляем фото + текст
    if image:
        await query.message.reply_photo(photo=image, caption=text)
    else:
        await query.message.reply_text(text)

    # После раздела — кнопка "Назад"
    await query.message.reply_text("Выберите другой раздел:", reply_markup=get_sections_keyboard())


async def main():
    import os
    TOKEN = os.getenv("BOT_TOKEN")  # Для Render

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    print("Bot started...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

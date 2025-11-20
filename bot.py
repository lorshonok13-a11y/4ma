import json
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton
)
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Load content
with open("content.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

SECTIONS = CONTENT["sections"]
BUY_URL = CONTENT["buy_url"]
CONTACT_URL = CONTENT["contact_url"]
WELCOME_TEXT = CONTENT["welcome_text"]

# --- Keyboards ---
def main_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Выбрать раздел"))
    kb.add(KeyboardButton("Купить планер"))
    kb.add(KeyboardButton("Связаться с автором"))
    kb.add(KeyboardButton("Помощь"))
    return kb

def sections_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row = []
    for i, s in enumerate(SECTIONS, 1):
        row.append(KeyboardButton(s["title"]))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)
    kb.add(KeyboardButton("Назад"))
    return kb


# --- Handlers ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_keyboard())


@dp.message(F.text == "Выбрать раздел")
async def choose_section(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=sections_keyboard())


@dp.message(F.text == "Купить планер")
async def buy(message: types.Message):
    await message.answer(BUY_URL)


@dp.message(F.text == "Связаться с автором")
async def contact(message: types.Message):
    await message.answer(CONTACT_URL)


@dp.message(F.text == "Помощь")
async def help_message(message: types.Message):
    await message.answer("Выберите раздел — и я покажу пример заполнения.")


@dp.message(F.text == "Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_keyboard())


@dp.message(lambda msg: any(msg.text == s["title"] for s in SECTIONS))
async def show_section(message: types.Message):
    section = next(s for s in SECTIONS if s["title"] == message.text)
    text = section["text"]
    image = section["image"]

    if image:
        # If image path exists locally
        if os.path.exists(image):
            with open(image, "rb") as photo:
                await message.answer_photo(photo, caption=text)
        else:
            # If image = URL (you can use this later)
            await message.answer_photo(image, caption=text)
    else:
        await message.answer(text)


# --- Launcher ---
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))

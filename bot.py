
import json
import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN not set")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

with open("content.json", "r", encoding="utf-8") as f:
    CONTENT = json.load(f)

SECTIONS = CONTENT["sections"]
BUY_URL = CONTENT.get("buy_url")
CONTACT_URL = CONTENT.get("contact_url")
WELCOME_TEXT = CONTENT.get("welcome_text")

def build_menu_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("Выбрать раздел"))
    kb.add(KeyboardButton("Купить планер"))
    kb.add(KeyboardButton("Связаться с автором"))
    kb.add(KeyboardButton("Помощь"))
    return kb

def build_sections_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    row=[]
    for i,s in enumerate(SECTIONS,1):
        row.append(KeyboardButton(s["title"]))
        if i%2==0:
            kb.row(*row); row=[]
    if row: kb.row(*row)
    kb.add(KeyboardButton("Назад"))
    return kb

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=build_menu_keyboard())

@dp.message_handler(lambda m: m.text=="Выбрать раздел")
async def choose(message: types.Message):
    await message.answer("Выберите раздел:", reply_markup=build_sections_keyboard())

@dp.message_handler(lambda m: m.text=="Купить планер")
async def buy(message: types.Message):
    await message.answer(BUY_URL)

@dp.message_handler(lambda m: m.text=="Связаться с автором")
async def contact(message: types.Message):
    await message.answer(CONTACT_URL)

@dp.message_handler(lambda m: m.text=="Помощь")
async def help(message: types.Message):
    await message.answer("Выберите раздел и получите пример заполнения.")

@dp.message_handler(lambda m: m.text=="Назад")
async def back(message: types.Message):
    await message.answer("Главное меню:", reply_markup=build_menu_keyboard())

@dp.message_handler(lambda m: any(m.text==s["title"] for s in SECTIONS))
async def section(message: types.Message):
    s = next(x for x in SECTIONS if x["title"]==message.text)
    text = s["text"]
    img = s["image"]
    if img:
        try:
            await message.answer_photo(img, caption=text)
            return
        except:
            pass
    await message.answer(text)

if __name__=="__main__":
    executor.start_polling(dp, skip_updates=True)

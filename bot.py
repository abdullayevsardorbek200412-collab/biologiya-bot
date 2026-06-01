import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from claude_handler import ClaudeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
claude = ClaudeHandler()


@dp.message(CommandStart())
async def start_handler(message: Message):
    name = message.from_user.first_name
    await message.answer(
        f"Salom, {name}! 🧬\n\n"
        "Men <b>Biologiya AI Yordamchi</b>man!\n"
        "5-11 sinf biologiya darsliklariga asoslanib javob beraman.\n\n"
        "📚 <b>Nima qila olaman:</b>\n"
        "• Matnli savolga javob beraman\n"
        "• Rasmli test/savolni tahlil qilaman\n"
        "• PDF kitoblardan ma'lumot topaman\n\n"
        "❓ Savolingizni yozing yoki rasm yuboring!",
        parse_mode="HTML"
    )


@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "📖 <b>Qo'llanma:</b>\n\n"
        "1️⃣ <b>Matnli savol:</b> Shunchaki yozing\n"
        "2️⃣ <b>Rasmli test:</b> Rasm yuboring\n"
        "3️⃣ <b>Sinf ko'rsating:</b> 7-sinf. Fotosintez nima?\n\n"
        "🔢 <b>Sinflar:</b> 5, 6, 7, 8, 9, 10, 11",
        parse_mode="HTML"
    )


@dp.message(F.text)
async def text_handler(message: Message):
    await message.answer("🔍 Qidiryapman...")
    try:
        answer = await claude.answer_text_question(message.text)
        await message.answer(answer, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")


@dp.message(F.photo)
async def photo_handler(message: Message):
    await message.answer("🖼 Rasm tahlil qilinmoqda...")
    try:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        caption = message.caption or "Bu rasmda qanday savol bor? To'g'ri javobni toping."
        answer = await claude.answer_image_question(file_url, caption)
        await message.answer(answer, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Rasmni tahlil qilishda xatolik.")


async def main():
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

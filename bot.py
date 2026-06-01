import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ContentType
from aiogram.fsm.storage.memory import MemoryStorage
from claude_handler import ClaudeHandler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Tokens — .env fayldan oling
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
claude = ClaudeHandler()


# /start komandasi
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


# /help komandasi
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "📖 <b>Qo'llanma:</b>\n\n"
        "1️⃣ <b>Matnli savol:</b> Shunchaki yozing\n"
        "   Misol: <i>Mitoz bo'linish necha bosqichdan iborat?</i>\n\n"
        "2️⃣ <b>Rasmli test:</b> Rasm yuboring + (ixtiyoriy) savol yozing\n"
        "   Misol: Rasm yuboring → <i>Qaysi javob to'g'ri?</i>\n\n"
        "3️⃣ <b>Sinf bo'yicha:</b> Sinfingizni yozing\n"
        "   Misol: <i>7-sinf. Fotosintez nima?</i>\n\n"
        "🔢 <b>Sinflar:</b> 5, 6, 7, 8, 9, 10, 11",
        parse_mode="HTML"
    )


# Matnli savol
@dp.message(F.text)
async def text_handler(message: Message):
    user_question = message.text
    await message.answer("🔍 Qidiryapman...")

    try:
        answer = await claude.answer_text_question(user_question)
        await message.answer(answer, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qayta urinib ko'ring.")


# Rasmli savol (photo)
@dp.message(F.photo)
async def photo_handler(message: Message):
    await message.answer("🖼 Rasm tahlil qilinmoqda...")

    try:
        # Eng katta rasmni olish
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"

        # Rasm bilan birga caption bo'lsa uni ham yuborish
        caption = message.caption or "Bu rasmda qanday savol bor? To'g'ri javobni toping."

        answer = await claude.answer_image_question(file_url, caption)
        await message.answer(answer, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Rasmni tahlil qilishda xatolik. Qayta urinib ko'ring.")


# Document (PDF yoki rasm fayl)
@dp.message(F.document)
async def document_handler(message: Message):
    doc = message.document
    if doc.mime_type == "application/pdf":
        await message.answer(
            "📄 PDF qabul qilindi!\n"
            "Hozircha PDF yuklash admin tomonidan amalga oshiriladi.\n"
            "Admin bilan bog'laning: @admin"
        )
    else:
        await message.answer("❓ Faqat rasm yoki PDF yuboring.")


async def main():
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

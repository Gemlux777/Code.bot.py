import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import password, qr

logging.basicConfig(level=logging.INFO)


async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔐 Пароль", callback_data="menu_password"),
         InlineKeyboardButton(text="📱 QR-код", callback_data="menu_qr")],
    ])
    await message.answer(
        "Привет! Я умею:\n"
        "🔐 Генерировать надёжные пароли\n"
        "📱 Создавать QR-коды из ссылок и текста\n\n"
        "Выбери действие:",
        reply_markup=kb
    )


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.message.register(cmd_start, CommandStart())
    dp.include_router(password.router)
    dp.include_router(qr.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

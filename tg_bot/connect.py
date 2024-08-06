import asyncio
import logging
import sys
import aiohttp

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import tg_token
from tg_bot.generate_token import generate_hex_token

TOKEN = tg_token
API_URL = "http://localhost:8000/"

routers = [
    'new_telegram_user'
]

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработка команды /start. Добавить логику, если токен уже выдан.
    """
    user_name = message.from_user.first_name
    user_surname = message.from_user.last_name
    user_id = message.from_user.id
    token = await generate_hex_token()

    payload = {"tg_id": int(user_id), "tg_name": str(user_name), "tg_surname": str(user_surname), "token": token}
    print(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL + routers[0], json=payload) as response:
            if response.status == 200:
                await message.answer(f"Привет, {html.bold(user_name)}!\n\nТвой токен: {html.code(token)}\nПришли его в сообщения сообществу в VK.")
            else:
                await message.answer("Произошла ошибка. Попробуйте еще раз.")


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("Бот не принимает сообщений.")



async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
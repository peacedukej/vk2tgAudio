import asyncio
import logging
import sys
import aiohttp
import aio_pika
import json 

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from config import tg_token, RABBITURL, FAST_API_URL
from generate_token import generate_hex_token
from api_listener import rabbitmq_listener

TOKEN = tg_token
bot = Bot(token=TOKEN)
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
        async with session.post(FAST_API_URL + 'new_telegram_user', json=payload) as response:
            if response.status == 200:
                await message.answer(f"Привет, {html.bold(user_name)}!\n\nТвой токен: {html.code(token)}\nПришли его в сообщения сообществу в VK.")
            else:
                await message.answer("Произошла ошибка. Попробуйте еще раз.")


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("Бот не принимает сообщений.")

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    loop = asyncio.get_running_loop()

    rabbitmq_task = loop.create_task(rabbitmq_listener(bot, loop, RABBITURL, "telegram_queue"))

    await dp.start_polling(bot)
    await rabbitmq_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
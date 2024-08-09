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

from config import tg_token, RABBITMQ_URL
from tg_bot.generate_token import generate_hex_token

TOKEN = tg_token
API_URL = "http://localhost:8000/"
#RABBITMQ_URL = "amqp://guest:guest@localhost/"

routers = [
    'new_telegram_user'
]
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
        async with session.post(API_URL + routers[0], json=payload) as response:
            if response.status == 200:
                await message.answer(f"Привет, {html.bold(user_name)}!\n\nТвой токен: {html.code(token)}\nПришли его в сообщения сообществу в VK.")
            else:
                await message.answer("Произошла ошибка. Попробуйте еще раз.")


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.answer("Бот не принимает сообщений.")

async def rabbitmq_listener(loop):
    connection = await aio_pika.connect_robust(RABBITMQ_URL, loop=loop)
    channel = await connection.channel()

    queue = await channel.declare_queue("telegram_queue", auto_delete=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                request = json.loads(message.body)

                print(request)
                print(type(request))
                #valid_json = json.load(message.body.decode())
                #print(valid_json)
                tg_id = request['tg_id']
                #print(tg_id)
                #await bot.send_message(tg_id, "test message")
                audiofile = FSInputFile(request['filename'])
                await bot.send_audio(chat_id=tg_id, audio=audiofile)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # Запуск прослушивания RabbitMQ в отдельной задаче
    loop = asyncio.get_running_loop()
    rabbitmq_task = loop.create_task(rabbitmq_listener(loop))
    
    # And the run events dispatching
    await dp.start_polling(bot)



    # Ожидание завершения задачи RabbitMQ
    await rabbitmq_task

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
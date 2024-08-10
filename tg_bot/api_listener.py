# rabbitmq_listener.py
import aio_pika
import json
import os, asyncio
from aiogram.types import FSInputFile

async def connect_to_rabbitmq(loop, url, retries=5, delay=10):
    for i in range(retries):
        try:
            connection = await aio_pika.connect_robust(url, loop=loop)
            return connection
        except Exception as e:
            if i < retries - 1:
                print(f"Не удалось подключиться к RabbitMQ. Повторная попытка через {delay} секунд...")
                await asyncio.sleep(delay)
            else:
                print("Исчерпаны все попытки подключения к RabbitMQ.")
                raise e


async def rabbitmq_listener(bot, loop, rabbitmq_url, queue_name, retries=5, delay=10) -> None:
    connection = await connect_to_rabbitmq(url=rabbitmq_url, loop=loop)
    channel = await connection.channel()
    print("хуй")
    queue = await channel.declare_queue(queue_name, auto_delete=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                request = json.loads(message.body)
                tg_id = request['tg_id']
                file = FSInputFile(request['filename'])
                title=request["title"]
                perfomer=request["artist"]
                #audio_name = request["audio_name"]
                if await bot.send_audio(chat_id=tg_id, audio=file, title=title, performer=perfomer):
                    #print(": ", request['filename'])
                    os.remove(request['filename'])

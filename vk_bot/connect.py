import vk_api
import random
import re
import aiohttp
import asyncio
import requests
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode

from config import vk_token

API_URL = "http://localhost:8000/"

routers = [
    'new_vk_user'
]

vk_session = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk_session)

async def write_msg(user_id: int, message: str):
    #random_id = int(VkLongpollMode.GET_RANDOM_ID)
    random_id = random.randint(1, 1e6)
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': random_id  # Генерация случайного ID
    })

async def is_valid_hex_token(user_token: str, expected_length: int = 32) -> bool:
    if len(user_token) != expected_length or len(user_token) % 2 != 0:
        return False
    
    # Регулярное выражение для проверки 16-ричных символов
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    # Проверка на соответствие паттерну
    return bool(hex_pattern.match(user_token))

async def main() -> None:
    print("start_polling")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                '''
                в БД добавить флаг, что токен выдан или нет, в зависимости от этого поменять логику
                Добавить проверку на тип сообщения
                '''
                if await is_valid_hex_token(user_token=event.text):
                    id = event.user_id
                    response = requests.post(url=f"https://api.vk.com/method/users.get?user_ids={id}&access_token={vk_token}&v={5.199}")
                    user_get = response.json()
                    user_get = user_get['response'][0]

                    payload = {"token": event.text, "vk_id": event.user_id, "vk_name": user_get['first_name'], "vk_surname": user_get['last_name']}
                    async with aiohttp.ClientSession() as session:
                        async with session.post(API_URL + routers[0], json=payload) as response:
                            print("Response STATUS", response.status)
                            if response.status == 200:
                                await write_msg(event.user_id, "Успешно привязано")
                            if response.status == 404:
                                await write_msg(event.user_id, "Токен не найден")
                elif 30 < len(event.text) <= 34 and ' ' not in event.text:
                    await write_msg(event.user_id, "Токен не найден. Проверьте правильноcть написания токена.")
                else:
                    await write_msg(event.user_id, "Бот не отвечает на текстовые сообщения. Просто присылай мне аудиозаписи, и я перешлю их тебе в Telegram.")
                    
                

if __name__ == "__main__":
    asyncio.run(main())
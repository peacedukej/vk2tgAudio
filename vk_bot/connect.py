import vk_api
import random
import re
import aiohttp
import asyncio
import requests
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode

from config import vk_token

API_URL = "http://localhost:8000/"

vk_session = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk_session)

async def write_msg(user_id: int, message: str):
    #random_id = int(VkLongpollMode.GET_RANDOM_ID)
    random_id = random.randint(1, 1e6)
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': random_id 
    })

async def is_valid_hex_token(token: str, expected_length: int = 32) -> bool:
    if len(token) != expected_length or len(token) % 2 != 0:
        return False
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    return bool(hex_pattern.match(token))


async def get_vk_profile_info(vk_id: int) -> dict:
    response = requests.get(url=f"https://api.vk.com/method/users.get?user_ids={vk_id}&access_token={vk_token}&v={5.199}")
    user_get = response.json()
    user_get = user_get['response'][0]
    profile_data = {"vk_name": user_get['first_name'], "vk_surname": user_get['last_name']}
    return profile_data

async def get_audio_data(message_id: int) -> dict:
    response = requests.get(url=f"https://api.vk.com/method/messages.getById?message_ids={message_id}&access_token={vk_token}&v={5.199}")
    audio_data = response.json()["response"]["items"][0]["attachments"][0]["audio"]
    #audio_data = audio_data["response"]["items"][0]["attachments"][0]["audio"]["url"]
    url = audio_data["url"]
    filename = (url.split("/")[-1]).split("?")[0]
    print(filename)
    return {"url": url, "filename": filename}

async def download_mp3(url, filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open("music/"+filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {url}, status code: {response.status}")

async def db_response(type: str, router: str, data: dict) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            if type == 'post':
                async with session.post(API_URL + router, json=data) as response:
                    response_data = await response.json()
                    return response_data
            elif type == 'get':
                async with session.get(API_URL + router, params=data) as response:
                    response_data = await response.json()
                    return response_data
            else:
                raise ValueError("Unsupported request type: {}".format(type))
    except aiohttp.ClientError as e:
        print(f"HTTP request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None

async def main() -> None:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            #if event.to_me:
            id = event.user_id
            message_id = event.message_id
            print(message_id)
            if await is_valid_hex_token(token=event.text):
                """
                Пользователь прислал токен (по формату), проверяем наличие токена в БД
                """
                validate_token = await db_response(type='get', router='validate_token', data={'token': event.text})
                if validate_token["response_status"] == 200:
                    """
                    Если токен корректен и найден, то заносим данные пользователя в БД
                    """
                    
                    payload = await get_vk_profile_info(vk_id=id)
                    payload['token'] = event.text
                    payload['vk_id'] = id

                    response = await db_response(type='post', router='new_vk_user', data=payload)
                    if response['response_status'] == 200:
                        await write_msg(event.user_id, "Успешно привязано. Теперь просто отправляй мне музыку.")
                    else:
                        await write_msg(event.user_id, "Произошла ошибка c привязкой.")
                else:
                    await write_msg(event.user_id, "Токен не найден.") 
            elif event.attachments:
                """
                Если пользователь прислал аудио
                """
                validate_tg_id = await db_response(type='get', router='validate_tg_id', data={'vk_id': id})
                if validate_tg_id['response_status'] == 200:
                    """
                    и если у него связаны аккаунты (для текущего vk_id есть tg_id)
                    """
                    if event.attachments["attach1_type"] == "audio":
                        await write_msg(event.user_id, "Начинаю загрузку!")
                        audio_data = await get_audio_data(message_id=message_id)
                        if audio_data:
                            await download_mp3(url=audio_data["url"], filename=audio_data["filename"])
                            await db_response(type='post', router='send_audio', data={"vk_id": id, "filename": audio_data["filename"]})
                        await write_msg(event.user_id, "Загружено!")
                else:
                    await write_msg(event.user_id, "Ты прислал аудио, но ты еще не связал аккаунты.")
            else:
                await write_msg(event.user_id, "Я пока не умею обрабатывать другие текстовые запросы.")

if __name__ == "__main__":
    asyncio.run(main())
import vk_api
import random
import re
import aiohttp
import asyncio
import requests
import signal
from json.decoder import JSONDecodeError
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode

from config import vk_token, FAST_API_URL

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
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"https://api.vk.com/method/users.get?user_ids={vk_id}&access_token={vk_token}&v=5.199") as response:
            user_get = await response.json()
            user_get = user_get['response'][0]
            profile_data = {"vk_name": user_get['first_name'], "vk_surname": user_get['last_name']}
            return profile_data

async def get_audio_data(message_id: int, audio_numbers: list) -> list:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=f"https://api.vk.com/method/messages.getById?message_ids={message_id}&access_token={vk_token}&v=5.199") as response:
            if response.status == 200:
                audio_data = []
                for num in audio_numbers:
                    audio = (await response.json())["response"]["items"][0]["attachments"][num]["audio"]
                    if audio["url"] != "":
                        audio_data.append(audio)
                return audio_data
            else:
                return []

async def download_mp3(url, filename) -> bool:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                content_length = response.headers.get('Content-Length')
                
                if content_length:
                    content_length = int(content_length)
                    if content_length > 49 * 1024 * 1024:
                        print(f"File {filename} is too large to download. Size: {content_length / (1024 * 1024)} MB")
                        return False
                else:
                    print("Content-Length header is missing. Proceeding without size check.")

                with open("music/"+filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                print(f"Downloaded {filename}")
            else:
                print(f"Failed to download {url}, status code: {response.status}")
            return True

async def db_response(type: str, router: str, data: dict) -> dict:
    try:
        async with aiohttp.ClientSession() as session:
            if type == 'post':
                async with session.post(FAST_API_URL + router, json=data) as response:
                    response_data = await response.json()
                    return response_data
            elif type == 'get':
                async with session.get(FAST_API_URL + router, params=data) as response:
                    response_data = await response.json()
                    return response_data
            else:
                raise ValueError("Unsupported request type: {}".format(type))
    except aiohttp.ClientError as e:
        print(f"HTTP request failed: {e}")
    except aiohttp.ClientResponseError as e:
        print(f"Client response error: {e}")
    except asyncio.TimeoutError:
        print("Request timed out")
    except ValueError as e:
        print(f"Error: {e}")
    except JSONDecodeError:
        print("Failed to parse JSON response")
    return None


async def main() -> None:
    def shutdown():
        loop.stop()
        print("Bot stopped.")

    loop = asyncio.get_running_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)

    try:

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                id = event.user_id
                message_id = event.message_id
                print("message_id: ", message_id)
                print("event: ", event)
                print("attachments: ", event.attachments)
                if await is_valid_hex_token(token=event.text):
                    validate_token = await db_response(type='get', router='validate_token', data={'token': event.text})
                    if validate_token["response_status"] == 200:
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
                    validate_tg_id = await db_response(type='get', router='validate_tg_id', data={'vk_id': id})
                    if validate_tg_id['response_status'] == 200:
                        audio_numbers = []
                        for i in range(1, 10): 
                            if event.attachments.get(f"attach{i}_type") == "audio":
                                audio_numbers.append(i-1)  # Преобразование индекса с 1 на 0

                        if audio_numbers:        
                            await write_msg(event.user_id, "Начинаю загрузку!")
                            audio_data = await get_audio_data(message_id=message_id, audio_numbers=audio_numbers)
                            for item in audio_data:
                                print(item)
                                print(type(item))
                                if await download_mp3(url=item["url"], filename=item["track_code"]):
                                    await db_response(type='post', router='send_audio', data={"vk_id": id, "filename": item["track_code"], "title": item["title"], "artist": item["artist"]})
                                else:
                                    await write_msg(event.user_id, f"Файл {item['artist'] + '--' + item['title']} слишком большой (>50 MB)")
                            

                        elif "fwd" in event.attachments:
                            await write_msg(event.user_id, "Я пока не умею обрабатывать пересланные сообщения. Отправь аудиозапись напрямую.")

                        else:
                            await write_msg(event.user_id, "Я пока не умею обрабатывать такие сообщения.")
                    else:
                        await write_msg(event.user_id, "Ты прислал аудио, но ты еще не связал аккаунты.")
                else:
                    await write_msg(event.user_id, "Я пока не умею обрабатывать другие текстовые запросы.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Shutting down bot...")

if __name__ == "__main__":
    asyncio.run(main())
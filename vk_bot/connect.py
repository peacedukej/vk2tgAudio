import vk_api
import random
import re
from vk_api.longpoll import VkLongPoll, VkEventType, VkLongpollMode

from config import vk_token

vk_session = vk_api.VkApi(token=vk_token)
longpoll = VkLongPoll(vk_session)

def write_msg(user_id: int, message: str):
    #random_id = int(VkLongpollMode.GET_RANDOM_ID)
    random_id = random.randint(1, 1e6)
    print(random_id)
    vk_session.method('messages.send', {
        'user_id': user_id,
        'message': message,
        'random_id': random_id  # Генерация случайного ID
    })

def is_valid_hex_token(user_token: str, expected_length: int = 32) -> bool:
    # Проверка на четность длины и соответствие ожидаемой длине
    if len(user_token) != expected_length or len(user_token) % 2 != 0:
        return False
    
    # Регулярное выражение для проверки 16-ричных символов
    hex_pattern = re.compile(r'^[0-9a-fA-F]+$')
    
    # Проверка на соответствие паттерну
    return bool(hex_pattern.match(user_token))


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            '''
            в БД добавить флаг, что токен выдан или нет, в зависимости от этого поменять логику
            Добавить проверку на тип сообщения
            '''
            if is_valid_hex_token(user_token=event.text):
                write_msg(event.user_id, "Успешно привязано")
            else:
                write_msg(event.user_id, "Неверный формат токена")


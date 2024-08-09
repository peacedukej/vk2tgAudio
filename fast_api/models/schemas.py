from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

class NewTelegramUser(BaseModel):
    tg_id: int
    tg_name: str
    tg_surname: str
    token: str

class NewVKUser(BaseModel):
    vk_id: int
    vk_name: str
    vk_surname: str
    token: str

class AudioData(BaseModel):
    vk_id: int
    filename: str
    title: str
    artist: str

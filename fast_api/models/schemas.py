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
    #vk_patronymic: str
    token: str

# class GetUseData(BaseModel):
#     main_email: str
#     password: str
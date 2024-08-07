from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, insert, delete, update
from fast_api.models.core import User
from sqlalchemy.ext.asyncio import AsyncSession
import fast_api.models.schemas as schemas # Импортируем созданную модель

from fast_api.controllers.connect_postgres import get_db

router = APIRouter()

@router.post("/new_telegram_user")
async def new_tg_user(new_tg_user_data: schemas.NewTelegramUser, db: AsyncSession = Depends(get_db)):
    """
    Получаю имя и токен из TG Bot, отправляю в БД
    """
    select_id = select(User).where(User.tg_id == new_tg_user_data.tg_id)
    select_id_query = await db.execute(select_id)
    select_id_query_result = select_id_query.scalars().first() if select_id_query else None

    if select_id_query_result is None:
        new_tg_user_data_insert = insert(User).values(tg_id=new_tg_user_data.tg_id,
                                                    tg_name=new_tg_user_data.tg_name,
                                                    tg_surname=new_tg_user_data.tg_surname,
                                                    token=new_tg_user_data.token)
        await db.execute(new_tg_user_data_insert)
        await db.commit()
    else:
        new_tg_user_data_insert = update(User).where(User.tg_id == new_tg_user_data.tg_id).values(tg_id=new_tg_user_data.tg_id,
                                                                                                tg_name=new_tg_user_data.tg_name,
                                                                                                tg_surname=new_tg_user_data.tg_surname,
                                                                                                token=new_tg_user_data.token)
        await db.execute(new_tg_user_data_insert)
        await db.commit()

@router.post("/new_vk_user")
async def new_vk_user(new_vk_user_data: schemas.NewVKUser, db: AsyncSession = Depends(get_db)):
    """
    Получаю выданный токен и данные пользователя из ВК
    """

    new_vk_user_data_insert = update(User).where(User.token == new_vk_user_data.token).values(vk_id=new_vk_user_data.vk_id,
                                                                                            vk_name=new_vk_user_data.vk_name,
                                                                                            vk_surname=new_vk_user_data.vk_surname
    )

    await db.execute(new_vk_user_data_insert)
    await db.commit()
    return {"response_status": 200}

@router.get("/validate_token")
async def validate_token(token: str, db: AsyncSession = Depends(get_db)):
    token_select = await db.execute(select(User).where(User.token == token))
    token_select_result = token_select.scalars().first() if token_select else None
    if token_select_result is None:
        return {"response_status": 404}
    return {"response_status": 200}

@router.get("/validate_tg_id")
async def validate_tg_id(vk_id: int, db: AsyncSession = Depends(get_db)):
    tg_id_select = await db.execute(select(User).where(User.vk_id == vk_id))
    tg_id_select_result = tg_id_select.scalars().first() if tg_id_select else None
    if tg_id_select_result is None:
        return {"response_status": 404}
    return {"response_status": 200}

@router.post("/send_audio")
async def send_audio(vk_id: int, filename: str, db: AsyncSession = Depends(get_db)):
    tg_id_select = await db.execute(select(User).where(User.vk_id == vk_id))
    tg_id = tg_id_select.scalars().first() if tg_id_select else None

    """
    послать сообщение брокеру, которого слушает бот, отправить filename, tg_id
    после этого удалить отправленный файл
    """
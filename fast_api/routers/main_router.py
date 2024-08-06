from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select, insert, delete, update
from fast_api.models.core import User
from sqlalchemy.ext.asyncio import AsyncSession
import fast_api.models.schemas as schemas # Импортируем созданную модель

from fast_api.controllers.connect_postgres import get_db

router = APIRouter()

# @router.post("/tokens/")
# def create_token(user_data: schemas.UserData, db: AsyncSession = Depends(get_db)):
#     db_token = User(access_token=user_data.access_token, user_id=user_data.user_id)
#     db.add(db_token)
#     db.commit()
#     db.refresh(db_token)
#     return db_token

# @router.get("/tokens/{user_id}")
# def read_token(user_id: int, db: AsyncSession = Depends(get_db)):
#     return db.query(User).filter(User.user_id == user_id).first()

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

    token_select = select(User).where(User.token == new_vk_user_data.token)
    token_select_query = await db.execute(token_select)
    db_token_result = token_select_query.scalars().first()
    db_token = db_token_result.token if db_token_result else None
    if db_token is None:
        raise HTTPException(status_code=404)

    new_vk_user_data_insert = update(User).where(User.token == new_vk_user_data.token).values(vk_id=new_vk_user_data.vk_id,
                                                                                            vk_name=new_vk_user_data.vk_name,
                                                                                            vk_surname=new_vk_user_data.vk_surname
    )

    await db.execute(new_vk_user_data_insert)
    await db.commit()

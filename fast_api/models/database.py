from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

import sys
from pathlib import Path
# Добавляем путь к родительской директории
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from config import postgress_password, postgres_user, server_name

encoded_password = quote_plus(postgress_password)
SQLALCHEMY_DATABASE_URL = f"postgresql+asyncpg://{postgres_user}:{encoded_password}@localhost:5432/{server_name}"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

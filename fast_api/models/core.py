from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, UniqueConstraint, Index, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

#from postgres.models.database import Base
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    token = Column(String, nullable=True)

    tg_id = Column(Integer, nullable=True)
    tg_name = Column(String, nullable=True)
    tg_surname = Column(String, nullable=True)
    
    vk_id = Column(Integer, nullable=True)
    vk_name = Column(String, nullable=True)
    vk_surname = Column(String, nullable=True)
    #vk_patronymic = Column(String, nullable=True)

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, UniqueConstraint, Index, Text, TIMESTAMP, func
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

from postgres.models.database import Base
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    #author_id = Column(Integer, ForeignKey('authors.id'))
    login = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    main_email = Column(String, nullable=False, unique=True)
    value = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    patronymic = Column(String, nullable=True)
    avatar_path = Column(String, nullable=True)
    token = Column(String, nullable=True)
    __table_args__ = (
        Index('users_id_idx', 'id'),
    )

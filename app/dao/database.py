from datetime import datetime
from typing import Annotated

from sqlalchemy import func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column, class_mapper

from app.config import Config, load_config

config: Config = load_config()

engine = create_async_engine(config.db.url_db)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[datetime, mapped_column(server_default=func.now(), onupdate=datetime.now())]


class Base(AsyncAttrs, DeclarativeBase):
    __abstract___ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}s'

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}



# def connection(method):
#     async def wrapper(*args, **kwargs):
#         async with async_session_maker() as session:
#             try:
#                 return await method(*args, session=session, **kwargs)
#             except Exception as e:
#                 await session.rollback()
#                 raise e
#             finally:
#                 await session.close()
#
#     return wrapper

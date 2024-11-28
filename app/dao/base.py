from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.database import Base

T = TypeVar('T', bound=Base)


class BaseDAO(Generic[T]):
    model = type[T]

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, **filter_by):
        if filter_by:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar_one_or_none()
        return None

    @classmethod
    async def check_base(cls, session: AsyncSession):
        stmt = select(cls.model).limit(1)
        result = await session.execute(stmt)
        if result.all():
            return True
        return False

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[BaseModel]):
        values_list = [item.model_dump(exclude_unset=True) for item in instances]
        new_instances = [cls.model(**values) for values in values_list]
        session.add_all(new_instances)
        try:
            await session.flush()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instances
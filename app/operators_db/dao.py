from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.operators_db.models import Node, Operator
from app.operators_db.schemas import SNode

class NodeDAO(BaseDAO[Node]):
    model = Node

    @classmethod
    async def find_all(cls, session: AsyncSession):
        query = select(cls.model)
        result = await session.execute(query)
        return result.scalars().all()


class OperatorDAO(BaseDAO[Operator]):
    model = Operator

    @classmethod
    async def update_one_operator(cls, filter_by: dict, values_dict: dict, session: AsyncSession):
        values_dict = {k: v for k, v in values_dict.items() if v}
        try:
            stmt = (
                update(cls.model)
                .filter_by(**filter_by)
                .values(**values_dict)
            )
            result = await session.execute(stmt)
            await session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            print(f'Error {e}')
            raise e

    @classmethod
    async def select_by_node_id(cls, node_id: int, session: AsyncSession):
        stmt = select(cls.model).filter_by(node_id=node_id)
        result = await session.execute(stmt)
        if result:
            return result.scalars().all()
        return False

    @classmethod
    async def select_by_node_name(cls, name: str, session: AsyncSession):
        stmt = select(cls.model).join(Node).filter_by(name=name)
        result = await session.execute(stmt)
        if result:
            return result.scalars().all()
        return False
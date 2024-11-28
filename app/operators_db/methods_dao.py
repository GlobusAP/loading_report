from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.session_maker import connection
from app.operators_db.dao import NodeDAO, OperatorDAO
from app.utils.files import __get_operators


@connection(commit=True)
async def add_one_node(data: dict, session: AsyncSession):
    new_node = await NodeDAO.add(session=session, **data)
    return new_node.id


@connection(commit=True)
async def add_one_operator(data: dict, session: AsyncSession):
    new_operator = await OperatorDAO.add(session=session, **data)
    return new_operator.id


@connection(commit=False)
async def get_nodes(session: AsyncSession):
    nodes = await NodeDAO.find_all(session=session)
    return nodes


@connection(commit=False)
async def get_operator(data: dict, session: AsyncSession):
    operator = await OperatorDAO.find_one_or_none(session=session, **data)
    return operator


@connection(commit=True)
async def upd_operator(filter_dict: dict, values_dict: dict, session: AsyncSession):
    operator = await OperatorDAO.update_one_operator(filter_dict, values_dict, session=session)
    return operator


@connection(commit=True)
async def add_all_operators(session: AsyncSession):
    nodes = await get_nodes()
    operators = await __get_operators(nodes)
    new_operators = await OperatorDAO.add_many(session=session, instances=operators)
    return new_operators


@connection(commit=False)
async def check_base(session: AsyncSession):
    check = await OperatorDAO.check_base(session=session)
    return check


@connection(commit=False)
async def select_operators(node_id: int, session: AsyncSession):
    operators = await OperatorDAO.select_by_node_id(node_id=node_id, session=session)
    return operators


@connection(commit=False)
async def select_operators_by_name(name: str, session: AsyncSession):
    operators = await OperatorDAO.select_by_node_name(name=name, session=session)
    return operators

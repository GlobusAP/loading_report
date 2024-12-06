from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.session_maker import connection
from app.users.dao import UsersDAO


@connection(commit=False)
async def get_user(session: AsyncSession, **data: dict):
    user = await UsersDAO.find_one_or_none(session=session, **data)
    return user


@connection(commit=True)
async def add_user(session: AsyncSession, **data: dict):
    new_user = await UsersDAO.add(session=session, **data)
    return new_user.id


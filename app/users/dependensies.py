from datetime import datetime, timezone

from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError

from app.config import Config, load_config
from app.users.exceptions import TokenNoFoundException, TokenExpiredException
from app.users.methods_dao import get_user


def get_token(request: Request):
    token = request.cookies.get('users_access_token')
    if not token:
        raise TokenNoFoundException
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        config: Config = load_config()
        payload = jwt.decode(token, config.jwt_token.secret_key, algorithms=config.jwt_token.algorithm)
    except JWTError as e:
        if e.args == ('Signature has expired.',):
            raise TokenExpiredException
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Токен не валидный!')

    expire: str = payload.get('exp')
    expire_time = datetime.fromtimestamp(int(expire), tz=timezone.utc)
    if (not expire) or (expire_time < datetime.now(timezone.utc)):
        raise TokenExpiredException

    user_id: str = payload.get('sub')
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Не найден ID пользователя')

    # user = await get_user(id=user_id)
    # if not user:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='User not found')
    return True

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import Config, load_config
from app.users.methods_dao import get_user
from app.users.schemas import SUserRegister

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    config: Config = load_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(config.jwt_token.expire))
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, config.jwt_token.secret_key, algorithm=config.jwt_token.algorithm)
    return encode_jwt


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(user_data: SUserRegister):
    user = await get_user(name=user_data.name)
    if not user or not verify_password(user_data.password, hashed_password=user.hashed_password):
        return None
    return user


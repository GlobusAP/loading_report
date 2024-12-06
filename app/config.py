from dataclasses import dataclass
from environs import Env


@dataclass
class DB:
    name: str
    user: str
    password: str
    port: int
    host: str

    def __post_init__(self):
        self.url_db = f'postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


@dataclass
class JWT:
    secret_key: str
    algorithm: str
    expire: int


@dataclass
class Config:
    db: DB
    jwt_token: JWT


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path=path)
    return Config(
        db=DB(
            name=env('POSTGRES_NAME'),
            user=env('POSTGRES_USER'),
            password=env('POSTGRES_PASSWORD'),
            port=env('POSTGRES_PORT'),
            host=env('POSTGRES_HOST')
        ),
        jwt_token=JWT(
            secret_key=env('SECRET_KEY'),
            algorithm=env('ALGORITHM'),
            expire=env('ACCESS_TOKEN_EXPIRE_MINUTES')
        )
    )

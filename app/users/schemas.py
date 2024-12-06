from pydantic import BaseModel, Field


class SUserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    password: str = Field(..., min_length=4, max_length=50, description="Пароль, от 4 до 50 знаков")
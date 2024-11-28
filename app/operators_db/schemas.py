from pydantic import BaseModel, Field, ConfigDict, field_validator


class SNodeAdd(BaseModel):
    name: str = Field(default=..., min_length=7, description='Название узла')


class SNode(BaseModel):
    id: int
    name: str | None


class SOperatorAdd(BaseModel):
    tg_number: int
    name: str
    CIC: int = Field(default=..., gt=0, description='Должен быть больше 0')
    node_id: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str):
        if value.isdigit():
            raise ValueError
        return value


class SOperatorGet(BaseModel):
    node_id: int
    tg_number: int

    model_config = ConfigDict(from_attributes=True)


class SOperatorUpdate(SOperatorAdd):
    name: str | None = Field(default=None)
    CIC: int | None = Field(default=None)

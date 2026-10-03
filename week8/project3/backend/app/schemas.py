from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class TodoCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title is required")
        return value


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("title cannot be empty")
        return value


class TodoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

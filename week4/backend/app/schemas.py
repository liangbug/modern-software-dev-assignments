from pydantic import BaseModel, field_validator


def _not_blank(v: str) -> str:
    if not v.strip():
        raise ValueError("must not be blank")
    return v


class NoteCreate(BaseModel):
    title: str
    content: str

    @field_validator("title", "content")
    @classmethod
    def not_blank(cls, v: str) -> str:
        return _not_blank(v)


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

    @field_validator("title", "content")
    @classmethod
    def not_blank(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _not_blank(v)


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str] = []

    class Config:
        from_attributes = True


class ActionItemCreate(BaseModel):
    description: str

    @field_validator("description")
    @classmethod
    def not_blank(cls, v: str) -> str:
        return _not_blank(v)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True

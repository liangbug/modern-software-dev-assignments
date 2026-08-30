from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class TagRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class NoteRead(BaseModel):
    id: int
    title: str
    content: str
    tags: list[TagRead] = []

    class Config:
        from_attributes = True


class NoteListResult(BaseModel):
    items: list[NoteRead]
    total: int


class NoteSearchResult(BaseModel):
    items: list[NoteRead]
    total: int
    page: int
    page_size: int


class NoteExtractResult(BaseModel):
    tags: list[str]
    action_items: list[str]


class ActionItemCreate(BaseModel):
    description: str = Field(min_length=1, max_length=2000)


class ActionItemRead(BaseModel):
    id: int
    description: str
    completed: bool

    class Config:
        from_attributes = True


class ActionItemListResult(BaseModel):
    items: list[ActionItemRead]
    total: int


class BulkCompleteRequest(BaseModel):
    ids: list[int]

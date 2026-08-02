from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


def _require_non_blank(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("must not be blank")
    return stripped


class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1)

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, value: str) -> str:
        return _require_non_blank(value)


class NoteResponse(BaseModel):
    id: int
    content: str
    created_at: str


class ActionItemExtractRequest(BaseModel):
    text: str = Field(..., min_length=1)
    save_note: bool = False

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, value: str) -> str:
        return _require_non_blank(value)


class ActionItemResponse(BaseModel):
    id: int
    text: str


class ActionItemExtractResponse(BaseModel):
    note_id: Optional[int]
    items: list[ActionItemResponse]


class ActionItemListResponse(BaseModel):
    id: int
    note_id: Optional[int]
    text: str
    done: bool
    created_at: str


class ActionItemDoneRequest(BaseModel):
    done: bool = True


class ActionItemDoneResponse(BaseModel):
    id: int
    done: bool

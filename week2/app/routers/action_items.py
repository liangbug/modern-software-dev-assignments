from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from .. import db
from ..schemas import (
    ActionItemDoneRequest,
    ActionItemDoneResponse,
    ActionItemExtractRequest,
    ActionItemExtractResponse,
    ActionItemListResponse,
    ActionItemResponse,
)
from ..services.extract import extract_action_items, extract_action_items_llm


router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ActionItemExtractResponse)
def extract(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.post("/extract-llm", response_model=ActionItemExtractResponse)
def extract_llm(payload: ActionItemExtractRequest) -> ActionItemExtractResponse:
    note_id: Optional[int] = None
    if payload.save_note:
        note_id = db.insert_note(payload.text)

    items = extract_action_items_llm(payload.text)
    ids = db.insert_action_items(items, note_id=note_id)
    return ActionItemExtractResponse(
        note_id=note_id,
        items=[ActionItemResponse(id=i, text=t) for i, t in zip(ids, items)],
    )


@router.get("", response_model=list[ActionItemListResponse])
def list_all(note_id: Optional[int] = None) -> list[ActionItemListResponse]:
    if note_id is not None and db.get_note(note_id) is None:
        raise HTTPException(status_code=404, detail="note not found")
    rows = db.list_action_items(note_id=note_id)
    result = []
    for row in rows:
        data = dict(row)
        data["done"] = bool(data["done"])
        result.append(ActionItemListResponse(**data))
    return result


@router.post("/{action_item_id}/done", response_model=ActionItemDoneResponse)
def mark_done(action_item_id: int, payload: ActionItemDoneRequest) -> ActionItemDoneResponse:
    if db.get_action_item(action_item_id) is None:
        raise HTTPException(status_code=404, detail="action item not found")
    db.mark_action_item_done(action_item_id, payload.done)
    return ActionItemDoneResponse(id=action_item_id, done=payload.done)



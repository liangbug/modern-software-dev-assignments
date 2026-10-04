from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ActionItem
from ..schemas import (
    ActionItemCreate,
    ActionItemListResult,
    ActionItemRead,
    BulkCompleteRequest,
)

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("/", response_model=ActionItemListResult)
def list_items(
    completed: bool | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
) -> ActionItemListResult:
    page = max(page, 1)
    page_size = max(page_size, 1)

    count_query = select(func.count()).select_from(ActionItem)
    items_query = select(ActionItem)
    if completed is not None:
        count_query = count_query.where(ActionItem.completed == completed)
        items_query = items_query.where(ActionItem.completed == completed)

    total = db.execute(count_query).scalar_one()

    items_query = items_query.order_by(ActionItem.id.asc())
    items_query = items_query.limit(page_size).offset((page - 1) * page_size)
    rows = db.execute(items_query).scalars().all()

    return ActionItemListResult(
        items=[ActionItemRead.model_validate(row) for row in rows], total=total
    )


@router.post("/", response_model=ActionItemRead, status_code=201)
def create_item(payload: ActionItemCreate, db: Session = Depends(get_db)) -> ActionItemRead:
    item = ActionItem(description=payload.description, completed=False)
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)


@router.post("/bulk-complete", response_model=list[ActionItemRead])
def bulk_complete_items(
    payload: BulkCompleteRequest, db: Session = Depends(get_db)
) -> list[ActionItemRead]:
    items: list[ActionItem] = []
    missing_ids: list[int] = []
    for item_id in payload.ids:
        item = db.get(ActionItem, item_id)
        if item is None:
            missing_ids.append(item_id)
            continue
        item.completed = True
        db.add(item)
        items.append(item)

    if missing_ids:
        # Trigger rollback of any staged completions above by propagating
        # the error out of the request-scoped session dependency.
        raise HTTPException(
            status_code=404,
            detail=f"Action item(s) not found: {sorted(missing_ids)}",
        )

    db.flush()
    for item in items:
        db.refresh(item)
    return [ActionItemRead.model_validate(item) for item in items]


@router.put("/{item_id}/complete", response_model=ActionItemRead)
def complete_item(item_id: int, db: Session = Depends(get_db)) -> ActionItemRead:
    item = db.get(ActionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    item.completed = True
    db.add(item)
    db.flush()
    db.refresh(item)
    return ActionItemRead.model_validate(item)

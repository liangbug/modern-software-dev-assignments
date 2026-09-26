from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Tag
from ..schemas import TagCreate, TagRead

router = APIRouter(prefix="/tags", tags=["tags"])


def get_or_create_tag(db: Session, name: str) -> Tag:
    name = name.strip()
    existing = db.execute(select(Tag).where(Tag.name == name)).scalar_one_or_none()
    if existing:
        return existing
    tag = Tag(name=name)
    db.add(tag)
    db.flush()
    return tag


@router.get("/", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    rows = db.execute(select(Tag).order_by(Tag.name)).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    existing = db.execute(select(Tag).where(Tag.name == payload.name)).scalar_one_or_none()
    if existing:
        return TagRead.model_validate(existing)

    tag = Tag(name=payload.name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return TagRead.model_validate(tag)

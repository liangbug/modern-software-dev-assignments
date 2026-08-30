from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note, Tag
from ..schemas import NoteRead, TagCreate, TagRead
from ..services.tags import get_or_create_tag

router = APIRouter(tags=["tags"])


@router.get("/tags", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)) -> list[TagRead]:
    rows = db.execute(select(Tag).order_by(Tag.name.asc())).scalars().all()
    return [TagRead.model_validate(row) for row in rows]


@router.post("/tags", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db)) -> TagRead:
    tag = get_or_create_tag(db, payload.name)
    return TagRead.model_validate(tag)


@router.delete("/tags/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    tag = db.get(Tag, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    db.delete(tag)
    db.flush()


@router.post("/notes/{note_id}/tags", response_model=NoteRead, status_code=201)
def attach_tag_to_note(note_id: int, payload: TagCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = get_or_create_tag(db, payload.name)
    if tag.id not in {t.id for t in note.tags}:
        note.tags.append(tag)
        db.add(note)
        db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/notes/{note_id}/tags/{tag_id}", response_model=NoteRead)
def detach_tag_from_note(note_id: int, tag_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    tag = db.get(Tag, tag_id)
    if not tag or tag.id not in {t.id for t in note.tags}:
        raise HTTPException(status_code=404, detail="Tag not attached to note")
    note.tags.remove(tag)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)

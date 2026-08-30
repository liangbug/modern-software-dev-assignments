from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead, NoteSearchResult

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("/", response_model=list[NoteRead])
def list_notes(db: Session = Depends(get_db)) -> list[NoteRead]:
    rows = db.execute(select(Note)).scalars().all()
    return [NoteRead.model_validate(row) for row in rows]


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=NoteSearchResult)
def search_notes(
    q: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort: str = "created_desc",
    db: Session = Depends(get_db),
) -> NoteSearchResult:
    page = max(page, 1)
    page_size = max(page_size, 1)

    filters = []
    if q:
        pattern = f"%{q.lower()}%"
        filters.append(
            or_(func.lower(Note.title).like(pattern), func.lower(Note.content).like(pattern))
        )

    count_query = select(func.count()).select_from(Note)
    items_query = select(Note)
    for condition in filters:
        count_query = count_query.where(condition)
        items_query = items_query.where(condition)

    total = db.execute(count_query).scalar_one()

    if sort == "title_asc":
        items_query = items_query.order_by(Note.title.asc())
    else:
        # created_desc: Note has no created_at column, so id (autoincrement)
        # is used as a proxy for insertion order.
        items_query = items_query.order_by(Note.id.desc())

    items_query = items_query.limit(page_size).offset((page - 1) * page_size)
    rows = db.execute(items_query).scalars().all()

    return NoteSearchResult(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)


@router.put("/{note_id}", response_model=NoteRead)
def update_note(note_id: int, payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.title = payload.title
    note.content = payload.content
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.flush()

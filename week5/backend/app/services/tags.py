from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Tag


def get_or_create_tag(db: Session, name: str) -> Tag:
    """Return the existing Tag matching `name` (case-insensitive), or create one."""
    existing = db.execute(select(Tag).where(Tag.name.ilike(name))).scalars().first()
    if existing:
        return existing
    tag = Tag(name=name)
    db.add(tag)
    db.flush()
    db.refresh(tag)
    return tag


def get_or_create_tags(db: Session, names: list[str]) -> list[Tag]:
    tags: list[Tag] = []
    seen_ids: set[int] = set()
    for name in names:
        tag = get_or_create_tag(db, name)
        if tag.id not in seen_ids:
            seen_ids.add(tag.id)
            tags.append(tag)
    return tags


def sync_note_tags_from_content(db: Session, note, hashtag_names: list[str]) -> None:
    """Attach tags parsed from hashtags to a note, without removing existing tags."""
    if not hashtag_names:
        return
    new_tags = get_or_create_tags(db, hashtag_names)
    existing_ids = {tag.id for tag in note.tags}
    for tag in new_tags:
        if tag.id not in existing_ids:
            note.tags.append(tag)
            existing_ids.add(tag.id)

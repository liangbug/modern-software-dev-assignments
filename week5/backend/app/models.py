from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    # note_id is covered by the composite PK's leading column, but tag_id needs
    # its own index for the reverse lookup used by "filter notes by tag".
    Index("ix_note_tags_tag_id", "tag_id"),
)


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    # Indexed: used by /notes/search sort=title_asc and case-insensitive match.
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (UniqueConstraint("name", name="uq_tags_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    notes = relationship("Note", secondary=note_tags, back_populates="tags")


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

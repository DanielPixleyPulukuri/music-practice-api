from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import SongKey
from app.database import Base

if TYPE_CHECKING:
    from app.models.practice_session import PracticeSession
    from app.models.user import User


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_number: Mapped[int | None] = mapped_column(nullable=True)
    title: Mapped[str] = mapped_column(nullable=False)

    original_key: Mapped[SongKey] = mapped_column(
        Enum(SongKey),
        nullable=False,
    )

    playing_key: Mapped[SongKey] = mapped_column(
        Enum(SongKey),
        nullable=False,
    )

    bpm: Mapped[int | None] = mapped_column(nullable=True)

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="songs")

    practice_sessions: Mapped[list["PracticeSession"]] = relationship(
        back_populates="song", cascade="all, delete-orphan"
    )

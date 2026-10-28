from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.enums import SongKey
from app.schemas.practice_session import PracticeSessionResponse


class SongCreate(BaseModel):
    title: str
    original_key: SongKey
    book_number: int | None = None
    playing_key: SongKey | None = None
    bpm: int | None = Field(default=None, gt=0)
    notes: str | None = None


class SongUpdate(BaseModel):
    title: str | None = None
    original_key: SongKey | None = None
    book_number: int | None = None
    playing_key: SongKey | None = None
    bpm: int | None = Field(default=None, gt=0)
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def check_title(cls, data):
        required_fields = ("title", "original_key", "playing_key")

        if isinstance(data, dict):
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null")

        return data


class SongResponse(BaseModel):
    id: int
    book_number: int | None
    title: str
    original_key: SongKey
    playing_key: SongKey
    bpm: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SongDetailResponse(BaseModel):
    id: int
    book_number: int | None
    title: str
    original_key: SongKey
    playing_key: SongKey
    bpm: int | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
    practice_sessions: list[PracticeSessionResponse]

    model_config = ConfigDict(from_attributes=True)

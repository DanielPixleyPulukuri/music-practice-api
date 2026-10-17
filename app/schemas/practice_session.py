from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PracticeSessionCreate(BaseModel):
    song_id: int
    duration_minutes: int = Field(gt=0)
    notes: str | None = None
    practiced_at: datetime | None = None


class PracticeSessionUpdate(BaseModel):
    practiced_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    notes: str | None = None


class PracticeSessionResponse(BaseModel):
    id: int
    song_id: int
    practiced_at: datetime
    duration_minutes: int | None = Field(default=None, gt=0)
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

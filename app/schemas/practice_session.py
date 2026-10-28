from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PracticeSessionCreate(BaseModel):
    song_id: int
    duration_minutes: int = Field(gt=0)
    notes: str | None = None
    practiced_at: datetime | None = None


class PracticeSessionUpdate(BaseModel):
    practiced_at: datetime | None = None
    duration_minutes: int | None = Field(default=None, gt=0)
    notes: str | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_required_fields(cls, data):
        required_fields = ("practiced_at", "duration_minutes")

        if isinstance(data, dict):
            for field in required_fields:
                if field in data and data[field] is None:
                    raise ValueError(f"{field} cannot be null")

        return data


class PracticeSessionResponse(BaseModel):
    id: int
    song_id: int
    practiced_at: datetime
    duration_minutes: int | None = Field(default=None, gt=0)
    notes: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

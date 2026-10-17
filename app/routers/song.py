from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.core.enums import SongKey, SongSort
from app.core.security import get_current_user
from app.database import get_db
from app.models.song import Song
from app.models.user import User
from app.schemas.practice_session import PracticeSessionResponse
from app.schemas.song import SongCreate, SongDetailResponse, SongResponse, SongUpdate

router = APIRouter(prefix="/songs", tags=["Songs"])

db_dependency = Annotated[Session, Depends(get_db)]
current_user_dependency = Annotated[User, Depends(get_current_user)]


@router.get("/", response_model=list[SongResponse], status_code=status.HTTP_200_OK)
def get_songs(
    db: db_dependency,
    current_user: current_user_dependency,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    title: str | None = None,
    original_key: SongKey | None = None,
    sort_by: SongSort = SongSort.id,
    order: str = "asc",
):
    stmt = select(Song).where(Song.user_id == current_user.id)

    if title:
        stmt = stmt.where(Song.title.ilike(f"%{title}%"))

    if original_key:
        stmt = stmt.where(Song.original_key == original_key)

    sort_columns = {
        SongSort.id: Song.id,
        SongSort.title: Song.title,
        SongSort.bpm: Song.bpm,
        SongSort.created_at: Song.created_at,
    }

    if order == "desc":
        stmt = stmt.order_by(desc(sort_columns[sort_by]))
    else:
        stmt = stmt.order_by(sort_columns[sort_by])

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt).scalars().all()
    return result


@router.get("/{song_id}", response_model=SongResponse, status_code=status.HTTP_200_OK)
def get_song(db: db_dependency, song_id: int, current_user: current_user_dependency):
    stmt = select(Song).where(and_(Song.user_id == current_user.id, Song.id == song_id))
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )
    return result


@router.post("/", response_model=SongResponse, status_code=status.HTTP_201_CREATED)
def create_song(
    db: db_dependency, song_data: SongCreate, current_user: current_user_dependency
):
    song_dict = song_data.model_dump()
    if song_dict["playing_key"] is None:
        song_dict["playing_key"] = song_dict["original_key"]
    song = Song(**song_dict, user_id=current_user.id)

    db.add(song)
    db.commit()
    db.refresh(song)
    return song


@router.delete("/{song_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_song(db: db_dependency, song_id: int, current_user: current_user_dependency):
    stmt = select(Song).where(and_(Song.user_id == current_user.id, Song.id == song_id))
    result = db.execute(stmt).scalar_one_or_none()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )
    db.delete(result)
    db.commit()


@router.patch("/{song_id}", response_model=SongResponse, status_code=status.HTTP_200_OK)
def update_song(
    db: db_dependency,
    song_id: int,
    song_data: SongUpdate,
    current_user: current_user_dependency,
):
    stmt = select(Song).where(and_(Song.user_id == current_user.id, Song.id == song_id))
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )

    song_dict = song_data.model_dump(exclude_unset=True)

    for key, value in song_dict.items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)
    return result


@router.get(
    "/{song_id}/practice-sessions",
    response_model=list[PracticeSessionResponse],
    status_code=status.HTTP_200_OK,
)
def get_song_practice_sessions(
    db: db_dependency, song_id: int, current_user: current_user_dependency
):
    stmt = select(Song).where(and_(Song.user_id == current_user.id, Song.id == song_id))
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )
    return result.practice_sessions


@router.get(
    "/{song_id}/details",
    response_model=SongDetailResponse,
    status_code=status.HTTP_200_OK,
)
def get_song_details(
    db: db_dependency, song_id: int, current_user: current_user_dependency
):
    stmt = select(Song).where(and_(Song.user_id == current_user.id, Song.id == song_id))
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {song_id} not found",
        )

    return result

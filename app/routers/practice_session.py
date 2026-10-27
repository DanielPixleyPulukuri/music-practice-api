from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.orm import Session

from app.core.enums import PracticeSessionSort
from app.core.security import get_current_user
from app.database import get_db
from app.models.practice_session import PracticeSession
from app.models.song import Song
from app.models.user import User
from app.schemas.practice_session import (
    PracticeSessionCreate,
    PracticeSessionResponse,
    PracticeSessionUpdate,
)

router = APIRouter(prefix="/practice-sessions", tags=["Practice Sessions"])

db_dependency = Annotated[Session, Depends(get_db)]
current_user_dependency = Annotated[User, Depends(get_current_user)]


@router.get(
    "/", response_model=list[PracticeSessionResponse], status_code=status.HTTP_200_OK
)
def get_practice_sessions(
    db: db_dependency,
    current_user: current_user_dependency,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    song_id: int | None = None,
    sort_by: PracticeSessionSort = PracticeSessionSort.id,
    order: str = "asc",
):
    stmt = (
        select(PracticeSession)
        .join(PracticeSession.song)
        .where(Song.user_id == current_user.id)
    )

    if song_id is not None:
        stmt = stmt.where(PracticeSession.song_id == song_id)

    sort_columns = {
        PracticeSessionSort.id: PracticeSession.id,
        PracticeSessionSort.practice_date: PracticeSession.practiced_at,
        PracticeSessionSort.duration: PracticeSession.duration_minutes,
        PracticeSessionSort.created_at: PracticeSession.created_at,
    }

    if order == "desc":
        stmt = stmt.order_by(desc(sort_columns[sort_by]))
    else:
        stmt = stmt.order_by(sort_columns[sort_by])

    stmt = stmt.offset(skip).limit(limit)

    result = db.execute(stmt).scalars().all()
    return result


@router.get(
    "/{practice_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
)
def get_practice_session(
    db: db_dependency, practice_id: int, current_user: current_user_dependency
):
    stmt = (
        select(PracticeSession)
        .join(PracticeSession.song)
        .where(
            and_(
                PracticeSession.id == practice_id,
                Song.user_id == current_user.id,
            )
        )
    )
    result = db.execute(stmt).scalar_one_or_none()

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Practice session with id {practice_id} not found ",
        )
    return result


@router.post(
    "/", response_model=PracticeSessionResponse, status_code=status.HTTP_201_CREATED
)
def create_practice_session(
    db: db_dependency,
    practice_data: PracticeSessionCreate,
    current_user: current_user_dependency,
):
    stmt = select(Song).where(
        and_(
            Song.user_id == current_user.id,
            Song.id == practice_data.song_id,
        )
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Song with id {practice_data.song_id} not found",
        )

    practice_dict = practice_data.model_dump()

    practice_session = PracticeSession(**practice_dict)

    db.add(practice_session)
    db.commit()
    db.refresh(practice_session)
    return practice_session


@router.patch(
    "/{practice_id}",
    response_model=PracticeSessionResponse,
    status_code=status.HTTP_200_OK,
)
def update_practice_session(
    db: db_dependency,
    practice_id: int,
    update_data: PracticeSessionUpdate,
    current_user: current_user_dependency,
):
    stmt = (
        select(PracticeSession)
        .join(PracticeSession.song)
        .where(
            and_(
                Song.user_id == current_user.id,
                PracticeSession.id == practice_id,
            )
        )
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Practice session with id {practice_id} not found",
        )

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(result, key, value)

    db.commit()
    db.refresh(result)
    return result


@router.delete("/{practice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_practice_session(
    db: db_dependency, practice_id: int, current_user: current_user_dependency
):
    stmt = (
        select(PracticeSession)
        .join(PracticeSession.song)
        .where(
            and_(
                PracticeSession.id == practice_id,
                Song.user_id == current_user.id,
            )
        )
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Practice session with id {practice_id} not found",
        )

    db.delete(result)
    db.commit()

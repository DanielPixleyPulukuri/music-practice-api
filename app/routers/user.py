from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/users", tags=["User"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(db: db_dependency, user_data: UserCreate):
    stmt = select(User).where(
        or_(User.username == user_data.username, User.email == user_data.email)
    )
    result = db.execute(stmt).scalar_one_or_none()

    if result is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )
    user_dict = user_data.model_dump()
    user_dict["hashed_password"] = hash_password(user_data.password)
    user_dict.pop("password")
    user = User(**user_dict)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(db: db_dependency, login_data: UserLogin):
    stmt = select(User).where(User.email == login_data.email)
    result = db.execute(stmt).scalar_one_or_none()

    if result is None or (
        not verify_password(login_data.password, result.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    token = create_access_token({"sub": str(result.id)})
    response = {"access_token": token, "token_type": "bearer"}
    return response


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

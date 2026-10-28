from fastapi import FastAPI

from app.routers.practice_session import router as practice_router
from app.routers.song import router as song_router
from app.routers.user import router as user_router

app = FastAPI()
app.include_router(song_router)
app.include_router(practice_router)
app.include_router(user_router)

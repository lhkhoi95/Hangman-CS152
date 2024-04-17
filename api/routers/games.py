from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.crud.games import get_games
from api.dependencies import get_db
from api.schemas.schemas import Difficulty
from api.utils.HangManAI import HangManAI


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.post("/")
async def retrieve_games(topic: str, difficulty: Difficulty, db: Session = Depends(get_db)):
    return get_games(db, topic, difficulty)

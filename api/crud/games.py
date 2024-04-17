from sqlalchemy.orm import Session
from api.schemas.schemas import Difficulty
from api.utils.HangManAI import HangManAI


def get_games(db: Session, topic: str, difficulty: Difficulty):
    hangmanAI = HangManAI()
    return hangmanAI.get_games(topic=topic, difficulty=difficulty)

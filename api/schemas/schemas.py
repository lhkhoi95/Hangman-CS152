from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, Json
from enum import Enum


class Game(BaseModel):
    id: int
    word: str
    definition: str


class Difficulty(str, Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"


class WordInfo(BaseModel):
    word: str
    definition: str

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, index=True)
    definition = Column(String)

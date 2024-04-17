import re
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Annotated, List
from api.crud import word_lists as crud
from api.dependencies import get_db
from api.schemas.schemas import WordList, Word
from api.utils.HangManAI import HangManAI

router = APIRouter(
    prefix="/word-lists",
    tags=["word-lists"],
)


@router.get("/", response_model=WordList)
async def create_generative_word_list(topic: Annotated[str, Query(min_length=2)], db: Session = Depends(get_db)):
    sanitized_topic = re.sub(r'\s+', ' ', topic).strip().title()
    hangmanAI = HangManAI()

    # If topic is invalid, raise an exception with the reason
    evaluated_topic = hangmanAI.evaluate_topic(sanitized_topic)
    if not evaluated_topic.isValid:
        raise HTTPException(
            status_code=400, detail=evaluated_topic.reason)

    # Check for repeated word list.
    word_list_exists = crud.get_user_word_list_by_title(
        db=db, title=sanitized_topic, uid=1)
    if word_list_exists:
        return word_list_exists

    # Ask AI models to generate one.
    return crud.create_generative_word_list(db=db, topic=sanitized_topic, user_id=1)


@router.get("/get-all", response_model=List[WordList])
async def get_all_word_lists(db: Session = Depends(get_db)):
    return crud.get_word_lists_by_uid(db=db, uid=1)


@router.get("/{word_list_id}", response_model=WordList)
async def get_word_list(word_list_id: int, db: Session = Depends(get_db)):
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")
    return db_word_list


@router.get("/{word_list_id}/more", response_model=WordList)
async def get_more_words(word_list_id: int, db: Session = Depends(get_db)):
    # Check if word_list_id exists
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=word_list_id)
    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    return crud.get_more_words(db=db, word_list_id=word_list_id)


@router.get("/words/{word_id}", response_model=Word)
async def get_word_info(word_id: int, db: Session = Depends(get_db)):
    db_word = crud.get_word_by_id(db, word_id=word_id)

    if db_word is None:
        raise HTTPException(
            status_code=404, detail=f"Word ID {word_id} not found")

    # Check if user has access to the word list
    db_word_list = crud.get_word_list_by_id(
        db, word_list_id=db_word.wordListId)

    if db_word_list is None:
        raise HTTPException(status_code=404, detail="Word list not found")

    # Check if definition, rootOrigin, usage, languageOrigin, partsOfSpeech, alternatePronunciation are empty
    if db_word.definition == '' or db_word.rootOrigin == '' or db_word.usage == '' or db_word.languageOrigin == '' or db_word.partsOfSpeech == '' or db_word.alternatePronunciation == '':
        try:
            word_info = crud.get_word_info(db=db, word_id=word_id)

            return word_info
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=400, detail="Error retrieving word info")

    return db_word

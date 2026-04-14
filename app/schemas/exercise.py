from typing import Dict, Any, Union
from pydantic import BaseModel
import uuid

from app.schemas.exercise_types.word_bank import WordBankQuestionData, WordBankAnswerData

class ExerciseBase(BaseModel):
    lesson_id: uuid.UUID
    exercise_type_id: uuid.UUID

# Base models for exercise types extending the Base
class WordBankExerciseCreate(ExerciseBase):
    question_data: WordBankQuestionData
    answer_data: WordBankAnswerData

class WordBankExerciseRead(WordBankExerciseCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True

# --- Fallback / Generic Schemas (for other unimplemented types) ---
class GenericExerciseCreate(ExerciseBase):
    question_data: Dict[str, Any] = {}
    answer_data: Dict[str, Any] = {}

class GenericExerciseRead(GenericExerciseCreate):
    id: uuid.UUID

    class Config:
        from_attributes = True

# --- Unions ---
# Pydantic will try WordBank schema first, then fallback to Generic dict if it fails
ExerciseCreate = Union[WordBankExerciseCreate, GenericExerciseCreate]
ExerciseRead = Union[WordBankExerciseRead, GenericExerciseRead]

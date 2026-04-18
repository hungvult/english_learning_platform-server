"""
Typed Pydantic schemas for all 7 polymorphic exercise types.
QuestionData models are sent to the client (no answers).
AnswerData models are only sent to admin/evaluation.
"""

from __future__ import annotations

from typing import Annotated, List, Literal, Union
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared option primitives
# ---------------------------------------------------------------------------

class OptionText(BaseModel):
    """A selectable text option."""
    id: str
    text: str


class OptionImage(BaseModel):
    """A selectable option with an image."""
    id: str
    text: str
    image_url: str


class WordBankItem(BaseModel):
    id: str
    text: str


# ---------------------------------------------------------------------------
# COMPLETE_CONVERSATION
# ---------------------------------------------------------------------------

class CompleteConversationQuestion(BaseModel):
    text: str                    # The prompt / dialogue line
    options: List[OptionText]


class CompleteConversationAnswer(BaseModel):
    correct_option_id: str


class CompleteConversationExercise(BaseModel):
    type: Literal["COMPLETE_CONVERSATION"]
    question_data: CompleteConversationQuestion
    answer_data: CompleteConversationAnswer


# ---------------------------------------------------------------------------
# ARRANGE_WORDS
# ---------------------------------------------------------------------------

class ArrangeWordsQuestion(BaseModel):
    tokens: List[str]            # Shuffled word tokens to arrange


class ArrangeWordsAnswer(BaseModel):
    correct_sequence: List[str]


class ArrangeWordsExercise(BaseModel):
    type: Literal["ARRANGE_WORDS"]
    question_data: ArrangeWordsQuestion
    answer_data: ArrangeWordsAnswer


# ---------------------------------------------------------------------------
# COMPLETE_TRANSLATION
# ---------------------------------------------------------------------------

class CompleteTranslationQuestion(BaseModel):
    source_sentence: str         # Original sentence shown to user
    text_template: str           # Template with {0}, {1} … blanks


class CompleteTranslationAnswer(BaseModel):
    correct_words: List[str]     # Words that fill the blanks in order


class CompleteTranslationExercise(BaseModel):
    type: Literal["COMPLETE_TRANSLATION"]
    question_data: CompleteTranslationQuestion
    answer_data: CompleteTranslationAnswer


# ---------------------------------------------------------------------------
# PICTURE_MATCH
# ---------------------------------------------------------------------------

class PictureMatchQuestion(BaseModel):
    word: str                    # Word or phrase to match
    options: List[OptionImage]


class PictureMatchAnswer(BaseModel):
    correct_option_id: str


class PictureMatchExercise(BaseModel):
    type: Literal["PICTURE_MATCH"]
    question_data: PictureMatchQuestion
    answer_data: PictureMatchAnswer


# ---------------------------------------------------------------------------
# TYPE_HEAR  (listen, then type what you hear)
# ---------------------------------------------------------------------------

class TypeHearQuestion(BaseModel):
    text: str                    # Sentence to convert to TTS audio


class TypeHearAnswer(BaseModel):
    correct_transcription: str


class TypeHearExercise(BaseModel):
    type: Literal["TYPE_HEAR"]
    question_data: TypeHearQuestion
    answer_data: TypeHearAnswer


# ---------------------------------------------------------------------------
# LISTEN_FILL  (play audio, pick words from bank)
# ---------------------------------------------------------------------------

class ListenFillQuestion(BaseModel):
    text: str                    # Sentence to convert to TTS audio
    word_bank: List[WordBankItem]


class ListenFillAnswer(BaseModel):
    correct_sequence_ids: List[str]  # Ordered IDs that match the audio


class ListenFillExercise(BaseModel):
    type: Literal["LISTEN_FILL"]
    question_data: ListenFillQuestion
    answer_data: ListenFillAnswer


# ---------------------------------------------------------------------------
# SPEAK_SENTENCE
# ---------------------------------------------------------------------------

class SpeakSentenceQuestion(BaseModel):
    sentence: str                # Sentence the user must speak


class SpeakSentenceAnswer(BaseModel):
    expected_text: str           # Used for STT comparison


class SpeakSentenceExercise(BaseModel):
    type: Literal["SPEAK_SENTENCE"]
    question_data: SpeakSentenceQuestion
    answer_data: SpeakSentenceAnswer


# ---------------------------------------------------------------------------
# Discriminated union — use as the single validator
# ---------------------------------------------------------------------------

ExerciseVariant = Annotated[
    Union[
        CompleteConversationExercise,
        ArrangeWordsExercise,
        CompleteTranslationExercise,
        PictureMatchExercise,
        TypeHearExercise,
        ListenFillExercise,
        SpeakSentenceExercise,
    ],
    # Pydantic v2 discriminator — requires 'type' literal in every variant
]

EXERCISE_TYPE_NAMES = [
    "COMPLETE_CONVERSATION",
    "ARRANGE_WORDS",
    "COMPLETE_TRANSLATION",
    "PICTURE_MATCH",
    "TYPE_HEAR",
    "LISTEN_FILL",
    "SPEAK_SENTENCE",
]

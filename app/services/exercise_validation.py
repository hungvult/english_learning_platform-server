import re
import uuid
from fastapi import HTTPException, status
from sqlmodel import Session
from pydantic import ValidationError

from app.models.exercise import ExerciseType
import app.schemas.exercise_types as ext

QUESTION_SCHEMA_MAP = {
    "COMPLETE_CONVERSATION": ext.CompleteConversationQuestion,
    "ARRANGE_WORDS": ext.ArrangeWordsQuestion,
    "COMPLETE_TRANSLATION": ext.CompleteTranslationQuestion,
    "PICTURE_MATCH": ext.PictureMatchQuestion,
    "LISTEN_FILL": ext.ListenFillQuestion,
}

ANSWER_SCHEMA_MAP = {
    "COMPLETE_CONVERSATION": ext.CompleteConversationAnswer,
    "ARRANGE_WORDS": ext.ArrangeWordsAnswer,
    "COMPLETE_TRANSLATION": ext.CompleteTranslationAnswer,
    "PICTURE_MATCH": ext.PictureMatchAnswer,
    "TYPE_HEAR": ext.TypeHearAnswer,
    "LISTEN_FILL": ext.ListenFillAnswer,
    "SPEAK_SENTENCE": ext.SpeakSentenceAnswer,
}

def validate_exercise_payload(db: Session, exercise_type_id: uuid.UUID, question_data: dict | None, answer_data: dict | None) -> tuple[dict | None, dict]:
    """
    Validates the dynamic JSON payloads for Exercises based on strict domain rules.
    1. Looks up the human-readable string type (e.g., COMPLETE_CONVERSATION)
    2. Validates structure dynamically using strictly typed Pydantic models
    3. Runs explicit cross-field business logic required for each exercise
    """
    exercise_type = db.get(ExerciseType, exercise_type_id)
    if not exercise_type:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"ExerciseType {exercise_type_id} does not exist"
        )
    
    type_name = exercise_type.name

    # 1. Null Checks for question_data
    if type_name in ("TYPE_HEAR", "SPEAK_SENTENCE"):
        if question_data is not None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"question_data must be null for {type_name}"
            )
        q_dict = None
        q_obj = None
    else:
        if question_data is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"question_data cannot be null for {type_name}"
            )
        
        # 2. Base Pydantic Validation for Question
        q_schema = QUESTION_SCHEMA_MAP.get(type_name)
        if not q_schema:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"No logic mapping defined for {type_name} question"
            )
        try:
            q_obj = q_schema.model_validate(question_data)
            q_dict = q_obj.model_dump()
            
            # Additional structural checks based on domain logic
            if type_name in ("COMPLETE_CONVERSATION", "PICTURE_MATCH"):
                if len(q_obj.options) < 2:
                    raise HTTPException(422, "options array must have a minimum length of 2")
            
            elif type_name == "ARRANGE_WORDS":
                if len(q_obj.tokens) < 2:
                    raise HTTPException(422, "tokens array must have a minimum length of 2")
            
            elif type_name == "LISTEN_FILL":
                if len(q_obj.word_bank) < 2:
                    raise HTTPException(422, "word_bank array must have a minimum length of 2")

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=e.errors()
            )

    # 3. Base Pydantic Validation for Answer
    if answer_data is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="answer_data cannot be null"
        )
    a_schema = ANSWER_SCHEMA_MAP.get(type_name)
    if not a_schema:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No logic mapping defined for {type_name} answer"
        )
    try:
        a_obj = a_schema.model_validate(answer_data)
        a_dict = a_obj.model_dump()
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )

    # 4. Cross-field Business Logic Inter-dependencies
    if type_name in ("COMPLETE_CONVERSATION", "PICTURE_MATCH"):
        valid_ids = {opt.id for opt in q_obj.options}
        if a_obj.correct_option_id not in valid_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"correct_option_id '{a_obj.correct_option_id}' does not exactly match any id present in question_data.options"
            )

    elif type_name == "COMPLETE_TRANSLATION":
        placeholders = set(re.findall(r"\{\d+\}", q_obj.text_template))
        if len(placeholders) != len(a_obj.correct_words):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Length of correct_words ({len(a_obj.correct_words)}) must precisely equal the count of unique placeholders ({len(placeholders)}) in text_template"
            )

    elif type_name == "ARRANGE_WORDS":
        if len(a_obj.correct_sequence) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="correct_sequence cannot be empty"
            )
        # Check subset or exact match
        token_counts = {}
        for t in q_obj.tokens:
            token_counts[t] = token_counts.get(t, 0) + 1
        
        seq_counts = {}
        for word in a_obj.correct_sequence:
            seq_counts[word] = seq_counts.get(word, 0) + 1
            
        for word, count in seq_counts.items():
            if token_counts.get(word, 0) < count:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Word '{word}' appears in correct_sequence more times than it exists in tokens, or does not exist at all"
                )

    elif type_name == "LISTEN_FILL":
        if len(a_obj.correct_sequence_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="correct_sequence_ids cannot be empty"
            )
        valid_ids = {item.id for item in q_obj.word_bank}
        for expected_id in a_obj.correct_sequence_ids:
            if expected_id not in valid_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"correct_sequence_ids element '{expected_id}' does not match any id in question_data.word_bank"
                )

    return q_dict, a_dict

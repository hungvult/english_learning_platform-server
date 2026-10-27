import uuid

import pytest
from fastapi import HTTPException
from sqlmodel import Session

from app.models.exercise import ExerciseType
from app.services.exercise_validation import validate_exercise_payload


def test_unknown_exercise_type_raises_422(session: Session):
    """Passing a non-existent exercise_type_id must raise 422."""
    random_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, random_id, None, {})
    assert exc_info.value.status_code == 422
    assert "does not exist" in exc_info.value.detail


# ---------------------------------------------------------------------------
# COMPLETE_CONVERSATION
# ---------------------------------------------------------------------------


def test_complete_conversation_valid(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["COMPLETE_CONVERSATION"]
    q_data = {
        "text": "Hello, how are you today?",
        "options": [
            {"id": "opt_1", "text": "I am fine, thank you!"},
            {"id": "opt_2", "text": "I have an apple."},
        ],
    }
    a_data = {"correct_option_id": "opt_1"}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert q_res["text"] == "Hello, how are you today?"
    assert len(q_res["options"]) == 2
    assert a_res["correct_option_id"] == "opt_1"


def test_complete_conversation_null_question_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_CONVERSATION"]
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, None, {"correct_option_id": "opt_1"})
    assert exc_info.value.status_code == 422
    assert "question_data cannot be null" in exc_info.value.detail


def test_complete_conversation_min_length_options(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_CONVERSATION"]
    q_data = {
        "text": "Prompt text",
        "options": [{"id": "opt_1", "text": "Single option"}],
    }
    a_data = {"correct_option_id": "opt_1"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "minimum length of 2" in exc_info.value.detail


def test_complete_conversation_invalid_correct_option_id(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_CONVERSATION"]
    q_data = {
        "text": "Where is the station?",
        "options": [
            {"id": "opt_1", "text": "Turn left at the corner."},
            {"id": "opt_2", "text": "It is raining."},
        ],
    }
    a_data = {"correct_option_id": "opt_999"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "does not exactly match any id" in exc_info.value.detail


# ---------------------------------------------------------------------------
# ARRANGE_WORDS
# ---------------------------------------------------------------------------


def test_arrange_words_valid(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["I", "love", "learning", "languages"]}
    a_data = {"correct_sequence": ["I", "love", "learning", "languages"]}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert q_res["tokens"] == ["I", "love", "learning", "languages"]
    assert a_res["correct_sequence"] == ["I", "love", "learning", "languages"]


def test_arrange_words_valid_subset(session: Session, exercise_types: dict[str, ExerciseType]):
    """ARRANGE_WORDS allows distractors in tokens."""
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["she", "likes", "apples", "bananas", "he"]}
    a_data = {"correct_sequence": ["she", "likes", "apples"]}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert a_res["correct_sequence"] == ["she", "likes", "apples"]


def test_arrange_words_min_tokens_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["single"]}
    a_data = {"correct_sequence": ["single"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "minimum length of 2" in exc_info.value.detail


def test_arrange_words_empty_correct_sequence_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["word1", "word2"]}
    a_data = {"correct_sequence": []}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "correct_sequence cannot be empty" in exc_info.value.detail


def test_arrange_words_word_not_in_tokens_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["I", "am", "happy"]}
    a_data = {"correct_sequence": ["I", "am", "sad"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "appears in correct_sequence more times" in exc_info.value.detail


def test_arrange_words_excess_frequency_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["ARRANGE_WORDS"]
    q_data = {"tokens": ["very", "good", "nice"]}
    a_data = {"correct_sequence": ["very", "very", "good"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "appears in correct_sequence more times" in exc_info.value.detail


# ---------------------------------------------------------------------------
# COMPLETE_TRANSLATION
# ---------------------------------------------------------------------------


def test_complete_translation_valid_single_placeholder(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_TRANSLATION"]
    q_data = {
        "source_sentence": "Chào buổi chiều",
        "text_template": "{0}",
    }
    a_data = {"correct_words": ["Good afternoon"]}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert a_res["correct_words"] == ["Good afternoon"]


def test_complete_translation_valid_multiple_placeholders(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_TRANSLATION"]
    q_data = {
        "source_sentence": "Tôi uống cà phê mỗi buổi sáng",
        "text_template": "I {0} coffee every {1}.",
    }
    a_data = {"correct_words": ["drink", "morning"]}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert len(a_res["correct_words"]) == 2


def test_complete_translation_mismatch_placeholder_count_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["COMPLETE_TRANSLATION"]
    q_data = {
        "source_sentence": "Tôi uống cà phê",
        "text_template": "I {0} {1}",
    }
    a_data = {"correct_words": ["drink"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "must precisely equal the count of unique placeholders" in exc_info.value.detail


# ---------------------------------------------------------------------------
# PICTURE_MATCH
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "prefix",
    ["images/", "/static/images/", "http://", "https://", "/media/"],
)
def test_picture_match_valid_prefixes(
    session: Session, exercise_types: dict[str, ExerciseType], prefix: str
):
    ex_type = exercise_types["PICTURE_MATCH"]
    q_data = {
        "word": "Coffee",
        "options": [
            {"id": "1", "text": "Cà phê", "image_url": f"{prefix}coffee.jpg"},
            {"id": "2", "text": "Trà", "image_url": f"{prefix}tea.jpg"},
        ],
    }
    a_data = {"correct_option_id": "1"}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert a_res["correct_option_id"] == "1"


def test_picture_match_invalid_image_url_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["PICTURE_MATCH"]
    q_data = {
        "word": "Coffee",
        "options": [
            {"id": "1", "text": "Cà phê", "image_url": "invalid/path/coffee.jpg"},
            {"id": "2", "text": "Trà", "image_url": "images/tea.jpg"},
        ],
    }
    a_data = {"correct_option_id": "1"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "image_url must start with" in exc_info.value.detail


def test_picture_match_empty_image_url_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["PICTURE_MATCH"]
    q_data = {
        "word": "Coffee",
        "options": [
            {"id": "1", "text": "Cà phê", "image_url": "   "},
            {"id": "2", "text": "Trà", "image_url": "images/tea.jpg"},
        ],
    }
    a_data = {"correct_option_id": "1"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "image_url cannot be empty" in exc_info.value.detail


def test_picture_match_option_matching_failure_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["PICTURE_MATCH"]
    q_data = {
        "word": "Coffee",
        "options": [
            {"id": "1", "text": "Cà phê", "image_url": "images/coffee.jpg"},
            {"id": "2", "text": "Trà", "image_url": "images/tea.jpg"},
        ],
    }
    a_data = {"correct_option_id": "non_existent_id"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "does not exactly match any id" in exc_info.value.detail


def test_picture_match_min_length_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["PICTURE_MATCH"]
    q_data = {
        "word": "Coffee",
        "options": [{"id": "1", "text": "Cà phê", "image_url": "images/coffee.jpg"}],
    }
    a_data = {"correct_option_id": "1"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "minimum length of 2" in exc_info.value.detail


# ---------------------------------------------------------------------------
# TYPE_HEAR
# ---------------------------------------------------------------------------


def test_type_hear_valid(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["TYPE_HEAR"]
    q_data = None
    a_data = {"correct_transcription": "Please listen carefully to the instruction."}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is None
    assert a_res["correct_transcription"] == "Please listen carefully to the instruction."


def test_type_hear_non_null_question_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["TYPE_HEAR"]
    q_data = {"text": "Should not be provided"}
    a_data = {"correct_transcription": "Test"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "question_data must be null for TYPE_HEAR" in exc_info.value.detail


def test_type_hear_missing_transcription_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["TYPE_HEAR"]
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, None, {})
    assert exc_info.value.status_code == 422


# ---------------------------------------------------------------------------
# LISTEN_FILL
# ---------------------------------------------------------------------------


def test_listen_fill_valid(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["LISTEN_FILL"]
    q_data = {
        "text": "apple juice please",
        "word_bank": [
            {"id": "w1", "text": "apple"},
            {"id": "w2", "text": "juice"},
            {"id": "w3", "text": "please"},
            {"id": "w4", "text": "banana"},
        ],
    }
    a_data = {"correct_sequence_ids": ["w1", "w2", "w3"]}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is not None
    assert a_res["correct_sequence_ids"] == ["w1", "w2", "w3"]


def test_listen_fill_min_word_bank_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["LISTEN_FILL"]
    q_data = {
        "text": "apple",
        "word_bank": [{"id": "w1", "text": "apple"}],
    }
    a_data = {"correct_sequence_ids": ["w1"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "minimum length of 2" in exc_info.value.detail


def test_listen_fill_empty_sequence_ids_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["LISTEN_FILL"]
    q_data = {
        "text": "apple juice",
        "word_bank": [{"id": "w1", "text": "apple"}, {"id": "w2", "text": "juice"}],
    }
    a_data = {"correct_sequence_ids": []}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "correct_sequence_ids cannot be empty" in exc_info.value.detail


def test_listen_fill_unmatched_sequence_id_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["LISTEN_FILL"]
    q_data = {
        "text": "apple juice",
        "word_bank": [{"id": "w1", "text": "apple"}, {"id": "w2", "text": "juice"}],
    }
    a_data = {"correct_sequence_ids": ["w1", "w999"]}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "does not match any id in question_data.word_bank" in exc_info.value.detail


# ---------------------------------------------------------------------------
# SPEAK_SENTENCE
# ---------------------------------------------------------------------------


def test_speak_sentence_valid(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["SPEAK_SENTENCE"]
    q_data = None
    a_data = {"expected_text": "Good morning, how may I help you?"}

    q_res, a_res = validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert q_res is None
    assert a_res["expected_text"] == "Good morning, how may I help you?"


def test_speak_sentence_non_null_question_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["SPEAK_SENTENCE"]
    q_data = {"prompt": "Not allowed"}
    a_data = {"expected_text": "Expected spoken sentence"}
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, a_data)
    assert exc_info.value.status_code == 422
    assert "question_data must be null for SPEAK_SENTENCE" in exc_info.value.detail


def test_speak_sentence_missing_expected_text_raises_422(
    session: Session, exercise_types: dict[str, ExerciseType]
):
    ex_type = exercise_types["SPEAK_SENTENCE"]
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, None, {})
    assert exc_info.value.status_code == 422


def test_null_answer_data_raises_422(session: Session, exercise_types: dict[str, ExerciseType]):
    ex_type = exercise_types["COMPLETE_CONVERSATION"]
    q_data = {
        "text": "Hello",
        "options": [{"id": "1", "text": "Hi"}, {"id": "2", "text": "Bye"}],
    }
    with pytest.raises(HTTPException) as exc_info:
        validate_exercise_payload(session, ex_type.id, q_data, None)
    assert exc_info.value.status_code == 422
    assert "answer_data cannot be null" in exc_info.value.detail

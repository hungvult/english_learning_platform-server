import os
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
import uuid

router = APIRouter()

# Audio files directory
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "audio")


@router.get("/{exercise_id}/audio")
def get_exercise_audio(exercise_id: uuid.UUID):
    """
    Serve an audio file for a listening exercise from local filesystem.
    Audio files are stored as static/audio/{exercise_id}.mp3
    """
    file_path = os.path.join(AUDIO_DIR, f"{exercise_id}.mp3")

    if not os.path.isfile(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=f"{exercise_id}.mp3",
    )

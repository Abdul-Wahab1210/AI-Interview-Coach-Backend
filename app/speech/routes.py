from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import tempfile
import os

from app.auth.utils import get_current_user
from app.database.models import User

router = APIRouter(prefix="/speech", tags=["speech"], dependencies=[Depends(get_current_user)])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No audio file provided")

    suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from app.ai.speech_to_text import transcribe_audio as stt
        text = stt(tmp_path)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}")
    finally:
        os.unlink(tmp_path)

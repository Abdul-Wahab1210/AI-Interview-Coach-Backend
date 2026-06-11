from faster_whisper import WhisperModel
from app.config import settings

_model = None


def get_whisper_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
    return _model


def transcribe_audio(file_path: str) -> str:
    model = get_whisper_model()
    segments, _ = model.transcribe(file_path)
    return " ".join(segment.text.strip() for segment in segments)

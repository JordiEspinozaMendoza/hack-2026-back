from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from faster_whisper import WhisperModel
from app.utils.video import stream_transcription

model = WhisperModel("base")
router = APIRouter()


class VideoRequest(BaseModel):
    url: str


@router.get("/transcribe")
def transcribe_stream(url: str):
    return StreamingResponse(stream_transcription(url), media_type="text/plain")

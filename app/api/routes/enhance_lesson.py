from fastapi import APIRouter
from app.utils.lesson import stream_enhance_lesson
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/enhance-lesson-stream")
def enhance_lesson_stream(transcript_name: str, lesson_name: str):
    return StreamingResponse(
        stream_enhance_lesson(transcript_name, lesson_name), media_type="text/plain"
    )

from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.lesson import stream_enhance_lesson
from fastapi.responses import StreamingResponse

router = APIRouter()


class EnhanceLessonRequest(BaseModel):
    course_id: str
    lesson_id: str
    lesson_name: str
    lesson_content: str


@router.post("/enhance-lesson-stream")
def enhance_lesson_stream(request: EnhanceLessonRequest):
    return StreamingResponse(
        stream_enhance_lesson(
            request.course_id,
            request.lesson_id,
            request.lesson_name,
            request.lesson_content,
        ),
        media_type="text/plain",
    )

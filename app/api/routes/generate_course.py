from fastapi import APIRouter
from app.utils.courses import get_course, stream_generate_course
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/generate-course-stream")
def generate_course(transcript_name: str):
    return StreamingResponse(
        stream_generate_course(transcript_name), media_type="text/plain"
    )

@router.get("/courses/{course_id}")
def generate_course(course_id: str):
    return get_course(course_id)
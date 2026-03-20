from fastapi import APIRouter
from app.utils.courses import stream_generate_course
from fastapi.responses import StreamingResponse

router = APIRouter()


@router.get("/generate-course-stream")
def generate_course(transcript_name: str):
    return StreamingResponse(
        stream_generate_course(transcript_name), media_type="text/plain"
    )

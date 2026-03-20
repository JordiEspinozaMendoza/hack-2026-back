from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.courses import get_course, stream_generate_course
from fastapi.responses import StreamingResponse

router = APIRouter()


class CourseCreate(BaseModel):
    course_id: str
    transcript_name: str
    title: str
    description: str


@router.post("/generate-course-stream")
def generate_course_stream(course_create: CourseCreate):
    return StreamingResponse(
        stream_generate_course(
            course_id=course_create.course_id,
            transcript_name=course_create.transcript_name,
            title=course_create.title,
            description=course_create.description,
        ),
        media_type="text/plain",
    )


@router.get("/courses/{course_id}")
def generate_course(course_id: str):
    return get_course(course_id)

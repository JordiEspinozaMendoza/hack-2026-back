from fastapi import APIRouter
from pydantic import BaseModel
from app.utils.quizes import create_quiz_from_lesson
from fastapi.responses import JSONResponse

router = APIRouter()


class QuizRequest(BaseModel):
    course_id: str
    lesson_content: str


@router.post("/generate-quiz")
def generate_quiz(quiz_request: QuizRequest):
    try:
        quiz = create_quiz_from_lesson(
            quiz_request.course_id, quiz_request.lesson_content
        )
        return JSONResponse(content=quiz)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

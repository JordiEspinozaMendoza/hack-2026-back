from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.course import CourseCreate, CourseResponse
from app.services.course_service import create_course, get_courses, get_course
from app.api.deps import get_db

router = APIRouter()

@router.post("/", response_model=CourseCreate)
def create(data: CourseCreate, db: Session = Depends(get_db)):
    return create_course(db, data.title, data.description, data.lectures)

@router.get("/", response_model=list[CourseResponse])
def read_all(db: Session = Depends(get_db)):
    return get_courses(db)

@router.get("/{course_id}", response_model=CourseResponse)
def read_one(course_id: int, db: Session = Depends(get_db)):
    return get_course(db, course_id)


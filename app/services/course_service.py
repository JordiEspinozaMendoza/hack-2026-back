from sqlalchemy.orm import Session
from app.models.course import Course
from app.models.lectures import Lecture

def create_course(db: Session, name: str, description: str, lectures: list):
    obj = Course(name=name, description=description)
    for lecture_data in lectures:
        lecture = Lecture(**lecture_data)
        db.add(lecture)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_courses(db: Session):
    return db.query(Course).all()

def get_course(db: Session, course_id: int):
    return db.query(Course).filter(Course.id == course_id).first()
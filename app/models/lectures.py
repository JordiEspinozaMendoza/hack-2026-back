from sqlalchemy import Column, Integer, String
from app.db.base import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    content = Column(String, index=True)
    course_id = Column(Integer, index=True)
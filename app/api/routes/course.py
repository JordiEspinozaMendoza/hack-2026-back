from fastapi import APIRouter, Depends
from pydantic import BaseModel, json

from app.api.deps import get_db
import redis

router = APIRouter()

redis_client = redis.Redis(host="localhost", port=6379, db=0)


class CourseCreate(BaseModel):
    course_id: str
    title: str
    description: str


class CourseResponse(BaseModel):
    course_id: str
    title: str
    description: str
    lessons: list[dict] = []


@router.post("/", response_model=CourseCreate)
def create(data: CourseCreate):
    if redis_client.exists(f"course:{data.course_id}"):
        raise Exception("Course with this ID already exists")

    redis_client.hset(
        f"course:{data.course_id}",
        mapping={"title": data.title, "description": data.description},
    )

    return redis_client.hgetall(f"course:{data.course_id}")


@router.get("/", response_model=list[CourseResponse])
def list_courses():
    course_keys = redis_client.keys("course:*")
    courses = []
    for key in course_keys:
        course_data = redis_client.hgetall(key)
        courses.append(
            CourseResponse(
                course_id=key.decode().split(":")[1],
                title=course_data[b"title"].decode(),
                description=course_data[b"description"].decode(),
            )
        )
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
def read(course_id: str):
    if not redis_client.exists(f"course:{course_id}"):
        raise Exception("Course not found")

    course_data = redis_client.hgetall(f"course:{course_id}")
    return CourseResponse(
        course_id=course_id,
        title=course_data[b"title"].decode(),
        description=course_data[b"description"].decode(),
        lessons=json.loads(course_data.get(b"lessons", b"[]").decode()),
    )

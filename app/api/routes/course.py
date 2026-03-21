from fastapi import APIRouter, Depends
from pydantic import BaseModel
import json

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
    quizes: list[dict] = []


@router.post("/courses", response_model=CourseCreate)
def create(data: CourseCreate):
    if redis_client.exists(f"course:{data.course_id}"):
        raise Exception("Course with this ID already exists")

    redis_client.hset(
        f"course:{data.course_id}",
        mapping={"title": data.title, "description": data.description},
    )

    return redis_client.hgetall(f"course:{data.course_id}")


@router.get("/courses", response_model=list[CourseResponse])
def list_courses():
    print("Listing courses from Redis...")
    course_keys = redis_client.keys("course:*")
    print(f"Found course keys in Redis: {course_keys}")
    courses = []
    for key in course_keys:
        course_data = redis_client.get(key)
        course_json = json.loads(course_data)
        print(f"Loaded course from Redis: {course_json}")
        courses.append(
            CourseResponse(
                course_id=key.decode().split(":")[1],
                title=course_json["title"],
                description=course_json["description"],
            )
        )
    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
def read(course_id: str):
    if not redis_client.exists(f"course:{course_id}"):
        raise Exception("Course not found")

    course_data = redis_client.hgetall(f"course:{course_id}")
    return CourseResponse(
        course_id=course_id,
        title=course_data[b"title"].decode(),
        description=course_data[b"description"].decode(),
        lessons=json.loads(course_data.get(b"lessons", b"[]").decode()),
        quizes=json.loads(course_data.get(b"quizes", b"[]").decode()),
    )

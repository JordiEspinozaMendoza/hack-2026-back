from fastapi import FastAPI
from app.api.routes import transcribe, generate_course, enhance_lesson, quizes, career_advice
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="My API", description="API documentation for my project", version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transcribe.router, prefix="", tags=["Transcription"])
app.include_router(generate_course.router, prefix="", tags=["Generate Course"])
app.include_router(enhance_lesson.router, prefix="", tags=["Enhance Lesson"])
app.include_router(quizes.router, prefix="", tags=["Quizes"])
app.include_router(career_advice.router, prefix="", tags=["Career Advice"])


@app.get("/")
def root():
    return {"message": "API is running 🚀"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}

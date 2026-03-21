from fastapi import APIRouter
from app.utils.user import stream_career_advice, ScoredTag
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List

router = APIRouter()

class CareerAdviceRequest(BaseModel):
    role: str
    scored_tags: List[ScoredTag] = []

@router.post("/career-advice")
async def career_advice_stream(request: CareerAdviceRequest):
    return StreamingResponse(
        stream_career_advice(request.role, request.scored_tags), media_type="text/plain"
    )

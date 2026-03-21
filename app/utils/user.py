from fastapi import APIRouter
from typing import Generator, List
from pydantic import BaseModel
import ollama
import json

router = APIRouter()

MODEL = "phi3"
MAX_LESSON_INPUT_CHARS = 2000
MAX_ENHANCED_OUTPUT_CHARS = 5000

class ScoredTag(BaseModel):
    tag: str
    score: int

def stream_career_advice(role: str, scored_tags: List[ScoredTag]):
    try:
        print(f"Generating Career Advice for {role} User with {scored_tags}")
        prompt = f"""
        You are a Manager with a high experience in giving career advice to other people based on their likes, dislikes, strengths and weaknesses. But you also consider the future with the current trends and technologies.
        Based on the following role and tags that are scored by how much lectures or quizzes that person has completed in courses.
        Describe how the role may or may not align with their scored topics of interest.
        Notice how many tags they have, any pattern in them.
        Recommend what they can focus on the most preffered topics, what roles can be a good match for him if he looks to change roles or how he can improve on his current role.
        Keep the initial response with a max lenght of {MAX_ENHANCED_OUTPUT_CHARS} characters.
        Role: {role}
        Scored Tags: {scored_tags}
        """

        stream = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_ctx": 8192,
                "temperature": 0.2,
                "num_predict": max(256, MAX_ENHANCED_OUTPUT_CHARS // 4),
            },
            stream=True,
        )

        career_advice_chunks = []
        output_chars = 0
        for chunk in stream:
            content = chunk.get("message", {}).get("content", "")
            if not content:
                continue

            remaining = MAX_ENHANCED_OUTPUT_CHARS - output_chars


            if remaining <= 0:
                break

            piece = content[:remaining]
            if not piece:
                continue

            career_advice_chunks.append(piece)
            output_chars += len(piece)
            yield piece

            # print("chunk: ", content)
            # print("remaining: ", remaining)
            # print('piece', piece)

            if output_chars >= MAX_ENHANCED_OUTPUT_CHARS:
                yield "\n\nTell me if you want me to continue\n"
                break

        career_advice = "".join(career_advice_chunks)
        return career_advice

    except Exception as e:
        print("Error in course generation:", e)
        # Print the line where the error occurred
        import traceback

        traceback.print_exc()
        yield f"\nERROR: {str(e)}\n"
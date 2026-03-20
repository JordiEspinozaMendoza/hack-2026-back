import ollama
import json
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

MODEL = "phi3"
MAX_LESSON_INPUT_CHARS = 2000
MAX_ENHANCED_OUTPUT_CHARS = 5000


def create_quiz_from_lesson(lesson_id: str, lesson_content: str) -> dict:
    prompt = f"""
    You are a quiz generation assistant.

    Based on the following lesson content, generate a quiz with 5 questions and multiple choice answers (3 options per question at least, with one correct answer).
    The "is_correct" field should be "true" for the correct option and "false" for the incorrect options.

    Return JSON: {{
        "quiz": [
            {{
                "question": "string",
                "options": [
                    {{"option": "string", "is_correct": "string"}},
                    {{"option": "string", "is_correct": "string"}},
                    {{"option": "string", "is_correct": "string"}},
                    {{"option": "string", "is_correct": "string"}}
                ]
            }},
            ...
        ]
    }}

    Lesson Content:
    {lesson_content}
    """

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"num_ctx": 8192, "temperature": 0.2},
    )

    if redis_client:
        redis_client.set(
            f"quiz:{lesson_id}", json.dumps(response["message"]["content"])
        )
        redis_client.close()

    return json.loads(response["message"]["content"])

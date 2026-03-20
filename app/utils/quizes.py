import ollama
import json
import redis
import uuid

redis_client = redis.Redis(host="localhost", port=6379, db=0)

MODEL = "phi3"
MAX_LESSON_INPUT_CHARS = 2000
MAX_ENHANCED_OUTPUT_CHARS = 5000


def create_quiz_from_lesson(course_id: str, lesson_content: str) -> dict:
    try:
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
            # Find the course id and add the quiz to the course cache if exists
            course_cache_key = f"course:{course_id}"
            cached_course = redis_client.get(course_cache_key)
            if cached_course:
                course_data = json.loads(cached_course)
                # Add the quiz inside of quizes field of the course cache
                course_data["quizes"] = course_data.get("quizes", {})
                quiz_id = str(uuid.uuid4())

                course_data["quizes"].append(
                    {
                        "id": quiz_id,
                        "name": f"Quiz for lesson {lesson_content[:30]}",
                        "content": json.loads(response["message"]["content"])["quiz"],
                    }
                )
                print("Updating course cache with new quiz...")
                redis_client.set(course_cache_key, json.dumps(course_data))

            redis_client.close()

        return json.loads(response["message"]["content"])
    except Exception as e:
        print("Error in quiz generation:", e)
        import traceback

        traceback.print_exc()
        raise Exception("Failed to generate quiz")

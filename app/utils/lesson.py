from typing import Generator
import ollama
import json
import redis

MODEL = "phi3"
MAX_LESSON_INPUT_CHARS = 2000
MAX_ENHANCED_OUTPUT_CHARS = 5000

redis_client = redis.Redis(host="localhost", port=6379, db=0)


def stream_enhance_lesson(
    lesson_id: str, lesson_name: str, lesson_content: str
) -> Generator[str, None, str]:
    try:
        # path = f"courses/{transcript_name}_course.json"
        # print(f"Opening course: {path}...")

        # with open(path, "r", encoding="utf-8") as f:
        #     transcript = f.read()

        # # Get the specific lesson content from the course JSON
        # course_data = json.loads(transcript)
        # lesson_content = None
        # for lecture in course_data.get("lectures", []):
        #     if lecture["title"] == lesson_name:
        #         lesson_content = lecture["description"]
        #         break
        # if not lesson_content:
        #     raise Exception(
        #         f"Lesson '{lesson_name}' not found in course '{transcript_name}'"
        #     )
        # Check if redis client is available and try to get enhanced lesson from cache
        if redis_client:
            print(f"Checking Redis cache for enhanced lesson with ID: {lesson_id}...")
        prompt = f"""
        You are a lesson enhancement assistant.

        Return a well-structured Markdown document.

        - Add a blank line after each heading.
        - Each bullet point must be on its own line.
        - NEVER put multiple sections on the same line.
        - DO NOT wrap in code blocks (```).
        - After each section, explicitly add a line break (\n).
        - The length of the enhanced lesson must be less than {MAX_ENHANCED_OUTPUT_CHARS} characters.

        ## Structure:

        ## Add an engaging title to the lesson

        ### Overview

        - Item

        ### Key Concepts

        - Item

        ### Examples

        - Item

        ### Applications

        - Item

        ### Summary

        - Item
        The title of the lesson is "{lesson_name}".
        ## Lesson Content:
        {lesson_content}

        If formatting is not respected, the answer is incorrect.
        """

        stream = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={
                "num_ctx": 8192,
                "temperature": 0.2,
            },
            stream=True,
        )

        enhanced_parts = []
        output_chars = 0
        for chunk in stream:
            content = chunk["message"]["content"]
            enhanced_parts.append(content)
            output_chars += len(content)

            yield content

            if output_chars >= MAX_ENHANCED_OUTPUT_CHARS:
                yield "\n\n⚠️ Output truncated due to length limit.\n"
                break

        enhanced_lesson = "".join(enhanced_parts)
        if redis_client:
            redis_client.set(f"enhanced_lesson:{lesson_id}", enhanced_lesson)
            redis_client.close()

        return enhanced_lesson

    except Exception as e:
        print("Error in course generation:", e)
        # Print the line where the error occurred
        import traceback

        traceback.print_exc()
        yield f"\nERROR: {str(e)}\n"

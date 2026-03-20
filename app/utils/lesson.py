from fastapi import APIRouter
from typing import Generator
import ollama
import json

router = APIRouter()

MODEL = "phi3"
MAX_LESSON_INPUT_CHARS = 2000
MAX_ENHANCED_OUTPUT_CHARS = 5000


def stream_enhance_lesson(
    transcript_name: str, lesson_name: str
) -> Generator[str, None, str]:
    try:
        path = f"courses/{transcript_name}_course.json"
        print(f"Opening course: {path}...")
        yield f"Loading course: {transcript_name}\n"

        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read()

        # Get the specific lesson content from the course JSON
        course_data = json.loads(transcript)
        lesson_content = None
        for lecture in course_data.get("lectures", []):
            if lecture["title"] == lesson_name:
                lesson_content = lecture["description"]
                break
        if not lesson_content:
            raise Exception(
                f"Lesson '{lesson_name}' not found in course '{transcript_name}'"
            )

        prompt = f"""
        You are a lesson enhancer assistant.
        Based on the following lesson content, enhance it by adding more details, examples, and explanations to make it more comprehensive and engaging for students.
        Feel free to expand on the concepts and provide additional insights. It is important to give the students a deeper understanding of the topic. Add relevant examples and practical applications to make the lesson more relatable and easier to grasp.
        Keep the final lesson under {MAX_ENHANCED_OUTPUT_CHARS} characters.
        Return the enhanced lesson as a markdown string. Please include new lines escaped as \\n in the output before any title hashtags. using H2 for headings, bullet points for lists, and bold for key terms.
        Lesson Content:
        {lesson_content}
        """

        yield "Enhancing lesson...\n"
        yield "\n===ENHANCED LESSON===\n"

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

        enhanced_parts = []
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

            enhanced_parts.append(piece)
            output_chars += len(piece)
            yield piece

            if output_chars >= MAX_ENHANCED_OUTPUT_CHARS:
                yield "\n\n[Lesson output truncated to configured limit]\n"
                break

        enhanced_lesson = "".join(enhanced_parts)
        yield "\n✔ Lesson enhancement done\n"
        return enhanced_lesson

    except Exception as e:
        print("Error in course generation:", e)
        # Print the line where the error occurred
        import traceback

        traceback.print_exc()
        yield f"\nERROR: {str(e)}\n"

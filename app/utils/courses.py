from pydantic import BaseModel
from typing import Generator
import ollama
import json
import time
import os
import redis

redis_client = redis.Redis(host="localhost", port=6379, db=0)

MODEL = "phi3"
MAX_RETRIES = 3
CHUNK_SIZE = 1000


def chunk_text(text, size=CHUNK_SIZE):
    return [text[i : i + size] for i in range(0, len(text), size)]


def ollama_json(prompt):
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        format="json",
        options={"num_ctx": 8192, "temperature": 0.2},
    )
    return response["message"]["content"]


def retry_json(prompt):
    for attempt in range(MAX_RETRIES):
        try:
            raw = ollama_json(prompt)
            return json.loads(raw)
        except Exception as e:
            time.sleep(1)

    raise Exception("Failed after retries")


def stream_generate_lectures(summaries) -> Generator[str, None, list]:
    yield "📚 Generating lectures (streaming)...\n"

    lectures = []

    chunk_size = max(1, len(summaries) // 3)
    grouped = [
        summaries[i : i + chunk_size] for i in range(0, len(summaries), chunk_size)
    ]

    for i, group in enumerate(grouped):
        yield f"\n🧠 Generating lecture {i+1}/{len(grouped)}...\n"

        content = "\n".join(group)

        prompt = f"""
        You are a lecture generator assistant.
        Based on the following summarized points, generate a lecture with a title and description.
        
        Return JSON: {{
            "title": "string",
            "description": "string"
        }}

        Content:
        {content}
        """

        data = retry_json(prompt)

        lectures.append({"title": data["title"], "description": data["description"]})
        yield "\n===LECTURE===\n"
        yield json.dumps(
            {"title": data["title"], "description": data["description"]}, indent=2
        )

        yield f"\n✔ Lecture {i+1} done\n"
    return lectures


def stream_generate_course(
    course_id: str, transcript_name: str, title: str, description: str
) -> Generator[str, None, dict]:
    try:
        path = f"transcriptions/{transcript_name}"
        print(f"Opening transcript: {path}...")
        yield f"Loading transcript: {transcript_name}\n"

        with open(path, "r", encoding="utf-8") as f:
            transcript = f.read()

        yield "Chunking transcript...\n"
        chunks = chunk_text(transcript)

        summaries = []

        # Check if redis client is available and try to get enhanced lesson from cache
        if redis_client:
            print(
                f"Checking Redis cache for enhanced course with ID: {transcript_name}..."
            )
            cached = redis_client.get(f"enhanced_course:{transcript_name}")
            if cached:
                yield "Found enhanced course in cache! Loading...\n"
                return json.loads(cached)

        # 🔹 Summaries
        for i, chunk in enumerate(chunks):
            yield f"🧠 Summarizing chunk {i+1}/{len(chunks)}...\n"

            prompt = f"""
            You are a helpful assistant.

            Summarize into bullet points.

            Return JSON:
            {{
              "summary": ["point 1", "point 2"]
            }}

            Transcript:
            {chunk}
            """

            data = retry_json(prompt)
            summaries.extend(data["summary"])

            yield f"Chunk {i+1} summary: {data['summary']}\n"

        os.makedirs("courses", exist_ok=True)
        lectures_generated = yield from stream_generate_lectures(summaries)

        output_path = f"courses/{transcript_name}_course.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"lectures": lectures_generated}, f, indent=2)

        if redis_client:
            redis_client.set(
                f"course:{course_id}",
                json.dumps(
                    {
                        "title": title,
                        "description": description,
                        "lectures": lectures_generated,
                    }
                ),
            )
            redis_client.close()
        yield f"\nSaved course to {output_path}\n"

    except Exception as e:
        print("Error in course generation:", e)
        # Print the line where the error occurred
        import traceback

        traceback.print_exc()
        yield f"\nERROR: {str(e)}\n"

import ollama
import json
import time
from pydantic import BaseModel


class Lecture(BaseModel):
    title: str
    description: str


class Course(BaseModel):
    lectures: list[Lecture]


MODEL = "phi3"
MAX_RETRIES = 3
CHUNK_SIZE = 3000


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
            print(f"Retry {attempt+1} failed:", e)
            time.sleep(1)

    raise Exception("Failed after retries")


def summarize_chunks(chunks):
    summaries = []

    for i, chunk in enumerate(chunks):
        print(f"🧠 Summarizing chunk {i+1}/{len(chunks)}")

        prompt = f"""
You are a helpful assistant.

Summarize the following transcript chunk into clear bullet points.
Remove filler words.
Focus on key ideas only.

Return JSON:
{{
  "summary": ["point 1", "point 2"]
}}

Transcript:
{chunk}
"""

        data = retry_json(prompt)
        summaries.extend(data["summary"])

    return summaries


def generate_lectures(summaries):
    print("📚 Generating lectures...")

    joined = "\n".join(summaries)

    prompt = f"""
You are a course generator.

Create structured lectures from the following summarized content.

STRICT RULES:
- Return ONLY valid JSON
- Do NOT add extra keys
- Do NOT explain anything

Schema:
{{
  "lectures": [
    {{
      "title": "string",
      "description": "string"
    }}
  ]
}}

Requirements:
- At least 3 lectures
- Logical progression
- No filler words

Content:
{joined}
"""

    data = retry_json(prompt)
    return Course.model_validate(data)


def generate_enhanced_lecture(lecture):
    print(f"✨ Enhancing lecture: {lecture.title}")

    prompt = f"""
You are a helpful assistant.
Enhance the following lecture by improving clarity, adding more text content, and making it more engaging.
STRICT RULES:
- Return ONLY valid JSON
- Do NOT add extra keys
- Do NOT explain anything

Schema:
{{
  "title": "string",
  "content": "string"
}}
Lecture:
{{
  "title": "{lecture.title}",
  "content": "{lecture.content}"
}}
"""

    data = retry_json(prompt)
    return Lecture.model_validate(data)


def main():
    with open("outputs/transcription.txt", "r", encoding="utf-8") as f:
        transcript = f.read()

    print("Chunking transcript...")
    chunks = chunk_text(transcript)

    summaries = summarize_chunks(chunks)

    course = generate_lectures(summaries)

    enhanced_lectures = []
    for lecture in course.lectures:
        enhanced = generate_enhanced_lecture(lecture)
        enhanced_lectures.append(enhanced)
    course.lectures = enhanced_lectures

    # Save
    with open("outputs/course.json", "w", encoding="utf-8") as f:
        f.write(course.model_dump_json(indent=2))

    print("Done! Saved to outputs/course.json")


if __name__ == "__main__":
    main()

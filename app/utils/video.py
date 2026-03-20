from fastapi import APIRouter
from faster_whisper import WhisperModel
import requests
import uuid
import os

model = WhisperModel("base")


def download_video(url: str) -> str:
    filename = f"temp_{uuid.uuid4()}.mp4"

    try:
        print(f"Downloading video from {url} to {filename}...")
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        print(f"Download completed: {filename}")
        return filename

    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")


def create_transcription_file():
    folder = "transcriptions"
    os.makedirs(folder, exist_ok=True)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(folder, f"{file_id}.txt")

    return file_path


def stream_transcription(url: str):
    print(f"Transcribing video: {url}...")
    video_path = download_video(url)
    file_path = create_transcription_file()

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            segments, _ = model.transcribe(video_path, beam_size=5)

            for segment in segments:
                line = f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}\n"

                f.write(line)
                f.flush()
                yield line

    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

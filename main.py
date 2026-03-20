from faster_whisper import WhisperModel
import time
import os

model = WhisperModel("base")

output_path = "outputs/transcription.txt"
os.makedirs("outputs", exist_ok=True)

start_time = time.perf_counter()

segments, info = model.transcribe("video.mp4")

with open(output_path, "w", encoding="utf-8") as f:
    for segment in segments:
        line = f"[{segment.start:.2f} - {segment.end:.2f}] {segment.text}\n"
        f.write(line)

end_time = time.perf_counter()

print(f"Total time: {end_time - start_time:.2f} seconds")
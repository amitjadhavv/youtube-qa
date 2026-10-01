"""Step 1: transcribe one local MIT OCW lecture video into timestamped chunks.

Source: MIT OpenCourseWare 6.0001 (CC BY-NC-SA 4.0) - https://ocw.mit.edu
Usage:  python transcribe.py [lecture_number]   (default: 5)
Input:  data/MIT6_0001F16_Lecture_XX_300k.mp4 (already downloaded)
Output: data/lecture_XX.json
"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

LECTURE = int(sys.argv[1]) if len(sys.argv) > 1 else 5
TITLE = "Lecture 5: Tuples, Lists, Aliasing, Mutability, and Cloning"  # manual metadata
VIDEO_URL = f"https://archive.org/download/MIT6.0001F16/MIT6_0001F16_Lecture_{LECTURE:02d}_300k.mp4"
DATA = Path("data")
video_path = DATA / f"MIT6_0001F16_Lecture_{LECTURE:02d}_300k.mp4"
out_path = DATA / f"lecture_{LECTURE:02d}.json"

if not video_path.exists():
    sys.exit(f"Video not found: {video_path}")

print("Loading Whisper model (first run downloads it)...")
model = WhisperModel("base", device="cpu", compute_type="int8")

print(f"Transcribing {video_path} ...")
segments, info = model.transcribe(str(video_path), vad_filter=True)

chunks = []
for seg in segments:
    chunks.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
    print(f"[{seg.start:7.1f}s] {seg.text.strip()}")

out_path.write_text(json.dumps({
    "source": "MIT OpenCourseWare 6.0001, Fall 2016 (CC BY-NC-SA 4.0)",
    "lecture": LECTURE,
    "title": TITLE,
    "video_url": VIDEO_URL,
    "language": info.language,
    "chunks": chunks,
}, indent=2), encoding="utf-8")
print(f"Saved {len(chunks)} chunks to {out_path}")

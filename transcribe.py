"""Transcribe local MIT OCW 6.0001 lecture videos into timestamped chunks.

Source: MIT OpenCourseWare 6.0001 (CC BY-NC-SA 4.0) - https://ocw.mit.edu
Usage:  python transcribe.py [lecture_number]   (default: 5)   - one lecture
        python main.py                                          - all lectures
Input:  data/MIT6_0001F16_Lecture_XX_300k.mp4 (already downloaded)
Output: data/lecture_XX.json
"""
import json
import sys
from pathlib import Path

from faster_whisper import WhisperModel

SOURCE = "MIT OpenCourseWare 6.0001, Fall 2016 (CC BY-NC-SA 4.0)"
DATA = Path("data")

# Titles from https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/resources/lecture-videos/
TITLES = {
    1: "Lecture 1: What is Computation?",
    2: "Lecture 2: Branching and Iteration",
    3: "Lecture 3: String Manipulation, Guess and Check, Approximations, Bisection",
    4: "Lecture 4: Decomposition, Abstraction, and Functions",
    5: "Lecture 5: Tuples, Lists, Aliasing, Mutability, and Cloning",
    6: "Lecture 6: Recursion and Dictionaries",
    7: "Lecture 7: Testing, Debugging, Exceptions, and Assertions",
    8: "Lecture 8: Object Oriented Programming",
    9: "Lecture 9: Python Classes and Inheritance",
    10: "Lecture 10: Understanding Program Efficiency, Part 1",
    11: "Lecture 11: Understanding Program Efficiency, Part 2",
    12: "Lecture 12: Searching and Sorting",
}


def video_path(lecture):
    return DATA / f"MIT6_0001F16_Lecture_{lecture:02d}_300k.mp4"


def json_path(lecture):
    return DATA / f"lecture_{lecture:02d}.json"


def load_model():
    print("Loading Whisper model (first run downloads it)...")
    return WhisperModel("base", device="cpu", compute_type="int8")


def transcribe_lecture(lecture, model):
    """Transcribe one lecture video and write data/lecture_XX.json."""
    video = video_path(lecture)
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    print(f"Transcribing {video} ...")
    segments, info = model.transcribe(str(video), vad_filter=True)

    chunks = []
    for seg in segments:
        chunks.append({"start": round(seg.start, 2), "end": round(seg.end, 2), "text": seg.text.strip()})
        print(f"[{seg.start:7.1f}s] {seg.text.strip()}")

    out = json_path(lecture)
    out.write_text(json.dumps({
        "source": SOURCE,
        "lecture": lecture,
        "title": TITLES[lecture],
        "video_url": f"https://archive.org/download/MIT6.0001F16/{video.name}",
        "language": info.language,
        "chunks": chunks,
    }, indent=2), encoding="utf-8")
    print(f"Saved {len(chunks)} chunks to {out}")


if __name__ == "__main__":
    lecture = int(sys.argv[1])
    if lecture not in TITLES:
        sys.exit(f"Unknown lecture {lecture}; expected one of {min(TITLES)}-{max(TITLES)}")
    try:
        transcribe_lecture(lecture, load_model())
    except FileNotFoundError as e:
        sys.exit(str(e))

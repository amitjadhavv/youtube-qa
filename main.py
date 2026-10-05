"""Transcribe every downloaded MIT 6.0001 lecture in data/ into data/lecture_XX.json.

Usage:  python main.py            # skips lectures whose JSON already exists
        python main.py --force    # re-transcribe everything
"""
import sys

from transcribe import TITLES, json_path, load_model, transcribe_lecture, video_path

force = "--force" in sys.argv[1:]

todo, missing, done = [], [], []
for lecture in sorted(TITLES):
    if not video_path(lecture).exists():
        missing.append(lecture)
    elif json_path(lecture).exists() and not force:
        done.append(lecture)
    else:
        todo.append(lecture)

if missing:
    print(f"No video file for lectures: {missing} (skipped)")
if done:
    print(f"Already transcribed: {done} (use --force to redo)")
if not todo:
    sys.exit("Nothing to transcribe.")

print(f"Transcribing lectures: {todo}")
model = load_model()
for i, lecture in enumerate(todo, 1):
    print(f"\n=== {TITLES[lecture]} ({i}/{len(todo)}) ===")
    transcribe_lecture(lecture, model)

print("\nAll done.")

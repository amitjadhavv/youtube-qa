"""Step 2: merge Whisper segments into ~30-60s windows with neighbor context.

Usage:  python chunk.py [lecture_number]   (default: every data/lecture_XX.json)
Input:  data/lecture_XX.json
Output: data/chunks_XX.json - list of windows; `text` is for display, `embed_text`
        (title + neighbor snippets + text) is what gets embedded/indexed.
"""
import json
import sys
from pathlib import Path

DATA = Path("data")
TARGET = 45.0    # close a window once it is at least this long (seconds)
MAX_LEN = 60.0   # never grow a window past this
OVERLAP = 1      # trailing segments repeated at the start of the next window
NEIGHBOR_CHARS = 200  # how much of the previous/next window to add as context


def make_windows(segments):
    windows, i = [], 0
    while i < len(segments):
        j = i + 1  # exclusive end index; always take at least one segment
        while j < len(segments):
            length = segments[j - 1]["end"] - segments[i]["start"]
            next_length = segments[j]["end"] - segments[i]["start"]
            if length >= TARGET or next_length > MAX_LEN:
                break
            j += 1
        windows.append((i, j))
        if j >= len(segments):
            break
        i = max(i + 1, j - OVERLAP)
    return windows


def chunk_lecture(path):
    lec = json.loads(path.read_text(encoding="utf-8"))
    segs = lec["chunks"]
    spans = make_windows(segs)
    texts = [" ".join(s["text"] for s in segs[i:j]) for i, j in spans]

    out = []
    for n, ((i, j), text) in enumerate(zip(spans, texts)):
        prev_tail = texts[n - 1][-NEIGHBOR_CHARS:] if n > 0 else ""
        next_head = texts[n + 1][:NEIGHBOR_CHARS] if n + 1 < len(texts) else ""
        embed_text = f"{lec['title']}\nEarlier: ...{prev_tail}\n{text}\nLater: {next_head}..."
        out.append({
            "lecture": lec["lecture"],
            "title": lec["title"],
            "video_url": lec["video_url"],
            "start": segs[i]["start"],
            "end": segs[j - 1]["end"],
            "text": text,
            "embed_text": embed_text,
        })
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1:
        paths = [DATA / f"lecture_{int(sys.argv[1]):02d}.json"]
    else:
        paths = sorted(DATA.glob("lecture_*.json"))
    if not paths:
        sys.exit("No data/lecture_XX.json files found. Run transcribe.py / main.py first.")

    for path in paths:
        if not path.exists():
            sys.exit(f"Not found: {path}")
        chunks = chunk_lecture(path)
        out_path = DATA / path.name.replace("lecture_", "chunks_")
        out_path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")
        lens = [c["end"] - c["start"] for c in chunks]
        print(f"{path.name}: {len(chunks)} chunks, {min(lens):.0f}-{max(lens):.0f}s "
              f"(avg {sum(lens) / len(lens):.0f}s) -> {out_path}")

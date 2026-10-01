# YouTube / Podcast Q&A

Scope: this repo is ONLY the YouTube/podcast Q&A app. Ignore unrelated topics.

## Goal
Transcribe videos/podcasts with Whisper, split the transcript into timestamped chunks, and answer questions with a link to the exact timestamp. The project is also a learning exercise in audio-to-text and time-stamped chunking.

## Owner context
Amit Jadhav. Comfortable with FastAPI and Docker. Has IBM/Coursera certificates in GenAI apps, RAG and vector databases. Explain new concepts briefly; do not over-explain FastAPI, Docker or basic RAG.

## Content source (legal)
Use only openly licensed material. Current source: MIT OpenCourseWare 6.0001 (Fall 2016), CC BY-NC-SA 4.0.
- Credit MIT OCW and link the license wherever content is shown.
- Non-commercial only: no ads, no selling access.
- Share derived works (transcripts) under the same CC BY-NC-SA 4.0 license.
- Do not scrape arbitrary YouTube videos; only use videos with a verified Creative Commons license.
- Video files come from archive.org/ocw.mit.edu, e.g. https://archive.org/download/MIT6.0001F16/MIT6_0001F16_Lecture_06_300k.mp4 (links not yet verified by download).

## Environment
- Windows, Python 3.10, venv at `.venv` (activate: `.venv\Scripts\activate`)
- Install: `pip install -r requirements.txt`
- Git repo on `main`. Keep `data/` (videos, models) out of git.

## Current status
- Done: venv, git, `transcribe.py` (faster-whisper "base", CPU int8; writes `data/lecture_XX.json`).
- `transcribe.py` has NOT been run or tested yet.
- Next: run it on lecture 6, check the JSON, then embeddings + vector search, then FastAPI endpoint.

## Data format
`data/lecture_XX.json`: `{source, lecture, video_url, language, chunks: [{start, end, text}]}` (seconds as floats).

## Planned architecture
1. Transcribe (`transcribe.py`) -> timestamped segments.
2. Chunk: merge segments into ~30-60s windows with slight overlap; keep `start`/`end` of each window.
3. Embed chunks and store in a vector DB (Chroma or FAISS to start).
4. FastAPI `/ask`: retrieve top-k chunks, have an LLM answer only from them, return the answer plus source links like `<video_url>#t=<start_seconds>`.
5. Later: Dockerize, simple web UI, support more lectures/podcasts.

## Working rules
- Build in small steps; get each step running before the next.
- Always cite timestamps from retrieved chunks; never invent them.
- If the answer is not in the transcript, say so.
- Keep dependencies minimal; add them to `requirements.txt`.
- Do not commit videos, audio, model files, `.venv` or API keys.

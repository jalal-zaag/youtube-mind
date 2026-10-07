# 1. Overview

**YouTube Mind** is an AI web app. You paste a YouTube video URL, get a summary of the video, and ask questions that are answered from the video's own content.

## Features

| Feature | Description |
|---|---|
| 🔗 URL input | Paste any YouTube link: `watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`, mobile/music links, or a bare 11-character video ID. |
| 📝 Summary | **Detailed** style (Overview / Key Points / Takeaways) with `[M:SS]` timestamps. Streams live. |
| 💬 Ask the video | Chat-style Q&A grounded in the transcript (RAG). Answers cite timestamps; sources link to that moment in the video. Supports follow-up questions. |
| 📜 Transcript | Full transcript with a keyword filter; each line links to its timestamp. |
| ⬇️ Export | Download summary (`.md`) and transcript (`.txt`). |

All responses are in **English** and summaries use the **Detailed** style. The language and summary-style selectors are commented out in `app.py`.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| LLM | `meta-llama/Llama-3.1-8B-Instruct` via **remote** Hugging Face Inference API |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim) via **remote** Hugging Face Inference API |
| Transcripts | TranscriptAPI.com (`YOUTUBE_TRANSCRIPT_API_KEY`) |
| Vector search | NumPy cosine similarity (in-memory) |
| Config | python-dotenv (`.env`) |
| Tests | pytest |

> No model runs locally. Every AI call is an HTTPS request to Hugging Face.

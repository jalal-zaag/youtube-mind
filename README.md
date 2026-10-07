# 🧠 YouTube Mind

Paste a YouTube link → get an AI summary → chat with the video.
Answers are grounded in the transcript and cite clickable timestamps.

- **UI:** Streamlit
- **AI:** Remote Hugging Face Inference API (free tier). No models are downloaded or run locally.
  - LLM: `meta-llama/Llama-3.1-8B-Instruct`
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- **Transcripts:** [TranscriptAPI.com](https://transcriptapi.com) (`YOUTUBE_TRANSCRIPT_API_KEY`)

## Features

| Feature | How it works |
|---|---|
| 📝 Summary | Concise / Detailed / Bullet styles, any output language. Long videos use **map-reduce** (chunk → notes → final summary) so they never overflow the model context. Streams live. |
| 💬 Q&A | **RAG**: transcript → overlapping time-aware chunks → remote embeddings → cosine search → LLM answers *only* from retrieved excerpts, citing `[M:SS]`. Follow-up questions use chat history. |
| 📜 Transcript | Searchable transcript, every line links to that moment in the video. |
| ⬇️ Export | Download summary (.md) and transcript (.txt). |

## Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # then fill in your keys
streamlit run app.py
```

## Architecture

```
youtube_mind/
├── app.py                         # Streamlit entry: page layout + user flows only
├── youtube_mind/
│   ├── config.py                  # Settings (env/.env), validated at startup
│   ├── container.py               # Composition root: wires services -> pipelines
│   ├── exceptions.py              # Domain errors, shown to users as friendly messages
│   ├── models.py                  # Dataclasses: Transcript, Segment, Chunk, ChatMessage...
│   ├── prompts.py                 # All prompt templates in one place
│   ├── services/                  # Talk to the outside world
│   │   ├── transcript_service.py  #   TranscriptAPI.com client
│   │   ├── llm_service.py         #   HF chat completion (stream + retries)
│   │   ├── embedding_service.py   #   HF feature-extraction embeddings
│   │   └── vector_store.py        #   In-memory cosine-similarity index
│   ├── pipelines/                 # Business logic (UI-agnostic, testable)
│   │   ├── summarizer.py          #   Single-pass / map-reduce summarisation
│   │   └── qa.py                  #   RAG question answering
│   ├── ui/
│   │   ├── components.py          #   Reusable Streamlit widgets
│   │   └── state.py               #   Typed session state
│   └── utils/                     # Pure helpers: URL parsing, chunking, timestamps
└── tests/                         # Unit tests (no network)
```

**Data flow**

```
URL ─► url_parser ─► TranscriptService ─► Transcript (cached 24h per video)
                                              │
              ┌───────────────────────────────┴──────────────────────┐
              ▼                                                      ▼
         Summarizer                                               VideoQA
  short: 1 LLM call                          chunk_segments ─► EmbeddingService ─► VectorStore
  long : map(chunks) ─► reduce(notes)        question ─► embed ─► top-k ─► LLM (streamed) + sources
```

Design choices:
- **Layered:** UI → pipelines → services. The pipelines don't import Streamlit, so the same code could back a FastAPI or CLI frontend.
- **Dependency injection** through `container.py`. You can swap the model, vector store, or transcript provider in one place.
- **Swap models without code changes:** set `HF_LLM_MODEL` / `HF_EMBEDDING_MODEL` in `.env`.
- **Cost-aware:** transcripts are cached per video, and the embedding index is built only once, on the first question.

## Configuration

See `.env.example`. Required: `HUGGINGFACEHUB_API_TOKEN`, `YOUTUBE_TRANSCRIPT_API_KEY`.

## Tests

```bash
python -m pytest -q
```

## Notes

- The Hugging Face free tier has small monthly credits. If they run out, the app shows a clear message. Options: wait for the monthly reset, use another token, or add credits.
- Videos without captions have no transcript and can't be processed.

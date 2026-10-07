# 2. Architecture

## Folder Structure

```
youtube_mind/
├── app.py                         # Streamlit entry point (page layout + user flows)
├── requirements.txt
├── .env / .env.example            # Secrets and optional overrides
├── .streamlit/config.toml         # Streamlit theme/server settings
├── docs/                          # Project documentation (this folder)
├── tests/                         # Unit tests (no network calls)
└── youtube_mind/                  # Core Python package
    ├── config.py                  # Settings loaded and validated from env
    ├── container.py               # Composition root: builds and wires all objects
    ├── exceptions.py              # Domain errors with user-friendly messages
    ├── models.py                  # Dataclasses: Transcript, Segment, Chunk, ChatMessage...
    ├── prompts.py                 # All LLM prompt templates
    ├── services/                  # Integrations with external systems
    │   ├── transcript_service.py  #   TranscriptAPI.com client
    │   ├── llm_service.py         #   HF chat completion (streaming + retries + error mapping)
    │   ├── embedding_service.py   #   HF embeddings (batched, normalised)
    │   └── vector_store.py        #   In-memory cosine-similarity index
    ├── pipelines/                 # Business logic (no Streamlit imports)
    │   ├── summarizer.py          #   Single-pass / map-reduce summarisation
    │   └── qa.py                  #   RAG question answering
    ├── ui/
    │   ├── components.py          #   Reusable Streamlit widgets
    │   └── state.py               #   Typed session state (AppState)
    └── utils/                     # Pure helper functions
        ├── url_parser.py          #   Extract video ID from a URL
        ├── chunking.py            #   Time-aware transcript chunking
        └── timefmt.py             #   Timestamp formatting / deep links
```

## Layers

```
┌──────────────────────────────────────────┐
│  UI  (app.py, ui/)                       │  Streamlit only: rendering + session state
├──────────────────────────────────────────┤
│  Pipelines  (pipelines/)                 │  Summarizer, VideoQA (business logic)
├──────────────────────────────────────────┤
│  Services  (services/)                   │  Transcript API, HF LLM, HF embeddings, vector store
├──────────────────────────────────────────┤
│  Core  (models, config, exceptions,      │  Shared data types, settings, helpers
│         prompts, utils)                  │
└──────────────────────────────────────────┘
```

Each layer depends only on the layers below it. Pipelines never import Streamlit, so the same logic could back a FastAPI server or a CLI.

## Data Flow

```
User pastes URL
      │
      ▼
url_parser.extract_video_id()
      │
      ▼
TranscriptService.fetch()  ──►  Transcript (segments + metadata)
      │                         cached 24h per video (st.cache_data)
      │
      ├──────────────► Summarizer.summarize()  ──► streamed summary
      │
      └──────────────► VideoQA.build_index()   ──► VideoIndex (on first question)
                              │
                       VideoQA.ask(question) ──► streamed answer + sources
```

## Design Decisions

| Decision | Why |
|---|---|
| **Composition root** (`container.py`) | All objects are created in one place (dependency injection), so a model, vector store, or transcript provider is swapped in one file. |
| **Domain exceptions** | Every expected failure (bad URL, no captions, invalid token, credits exhausted) becomes a `YouTubeMindError` with a readable message the UI shows via `st.error`. |
| **Prompts in one file** | Prompts can be tuned without touching logic. |
| **Config via env** | Models, chunk sizes, top-k, and timeouts are configurable in `.env` without code changes. |
| **Caching** | Transcripts are cached per video (saves API credits); the client container is cached per process; the RAG index is built once per video per session. |
| **Streaming** | Summary and answers stream token by token for a responsive UI. |
| **Retries** | LLM calls retry with exponential backoff on 429/5xx errors. |

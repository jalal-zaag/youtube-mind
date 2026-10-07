# 3. RAG System & Summarizer

## Q&A — Retrieval-Augmented Generation

The **"💬 Ask the video"** feature is a RAG pipeline (`youtube_mind/pipelines/qa.py`).

### Indexing (once per video, on the first question)

1. **Chunking** — `utils/chunking.py`
   - Transcript segments are grouped into chunks of ~**180 words**, with ~**40 words of overlap** between neighbours.
   - Segments are never split, so every chunk keeps exact `start` / `end` timestamps.
2. **Embedding** — `services/embedding_service.py`
   - Chunks are sent in batches of 32 to the remote HF model `all-MiniLM-L6-v2`.
   - Vectors (384-dim) are L2-normalised, so a dot product equals cosine similarity.
3. **Storing** — `services/vector_store.py`
   - Vectors are kept in a NumPy matrix inside `InMemoryVectorStore`.
   - The index lives in Streamlit session state (`AppState.index`).

### Answering (every question)

1. The question (plus the previous user question, for follow-ups like "why?") is embedded.
2. The **top-k** most similar chunks are retrieved (default 5, adjustable in the sidebar).
3. Retrieved chunks are sorted by time and given to the LLM as `[M:SS - M:SS] text` excerpts.
4. The last 4 chat turns are included so follow-up questions make sense.
5. The system prompt forces the model to:
   - answer **only** from the excerpts,
   - say clearly when the video doesn't cover the question (no guessing),
   - cite timestamps like `[3:15]`.
6. The answer streams to the UI, and the sources appear in an expander with clickable timestamp links.

### Vector Store Note

The vectors are **not stored in a vector database**. They are held **in RAM** and lost on page refresh, on loading another video, or on app restart. For a single video (~20–50 chunks), a brute-force NumPy search is instant, so a database isn't needed. See the roadmap for adding a persistent store such as ChromaDB.

## Summarizer — Map-Reduce (not RAG)

The summary uses the **whole** transcript, not retrieval (`youtube_mind/pipelines/summarizer.py`).

| Video length | Strategy |
|---|---|
| ≤ 3,000 words | **Single pass**: the full timestamped transcript goes to the LLM in one call. |
| > 3,000 words | **Map-reduce**: split into ~2,500-word parts → each part condensed into bullet notes (map) → notes merged into the final summary (reduce). |

This keeps any video length within the model's context window. The transcript is rendered as `[M:SS] text` lines (~30 s each), so the summary can include timestamps.

## Key Parameters

| Parameter | Default | Env variable |
|---|---|---|
| Q&A chunk size | 180 words | `QA_CHUNK_WORDS` |
| Q&A chunk overlap | 40 words | `QA_CHUNK_OVERLAP_WORDS` |
| Top-k passages | 5 | `QA_TOP_K` |
| Single-pass limit | 3,000 words | `SINGLE_PASS_WORD_LIMIT` |
| Map chunk size | 2,500 words | `SUMMARY_CHUNK_WORDS` |
| Temperature | 0.3 | `LLM_TEMPERATURE` |
| Max new tokens | 1,024 | `LLM_MAX_NEW_TOKENS` |

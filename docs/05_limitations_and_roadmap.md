# 5. Limitations, Troubleshooting & Roadmap

## Known Limitations

- **Free-tier credits** — Hugging Face's free monthly inference credits are small. One long-video summary plus indexing uses a noticeable share.
- **In-memory vectors** — the RAG index is not persisted; it is rebuilt (and re-embedded) after a refresh or restart.
- **One video at a time** — Q&A can't search across several videos.
- **Captions required** — videos without captions/transcripts can't be processed.
- **Vector-only retrieval** — no keyword (hybrid) search or re-ranking.
- **Fixed output** — the language and summary-style selectors are disabled; output is always English and the Detailed summary style.

## Troubleshooting

| Message in the app | Cause | Fix |
|---|---|---|
| *Free Hugging Face Inference credits … used up* | HTTP 402 from HF | Wait for monthly reset, use another token, or add credits |
| *HUGGINGFACEHUB_API_TOKEN is invalid* | HTTP 401 from HF | Create a new token |
| *Token lacks permission* | HTTP 403 from HF | Enable "Make calls to Inference Providers" on the token |
| *Model … not served by any Inference Provider* | Model unavailable | Set another model in `HF_LLM_MODEL` |
| *YOUTUBE_TRANSCRIPT_API_KEY is invalid* | HTTP 401 from TranscriptAPI | Check the key in `.env` |
| *Transcript API credits are used up* | HTTP 402 from TranscriptAPI | Top up credits |
| *No transcript is available* | Video has no captions | Try another video |
| *Could not find a YouTube video ID* | Unsupported URL | Paste a normal YouTube video link |

## Roadmap

- [ ] Persistent vector database (ChromaDB/FAISS) in a `vector_db/` folder, so each video is embedded only once
- [ ] Multi-video library: search and ask across all loaded videos
- [ ] Hybrid retrieval (BM25 + vectors) and re-ranking
- [ ] Re-enable multi-language responses and summary styles
- [ ] FastAPI backend reusing the same `pipelines/` layer
- [ ] Docker image for one-command deployment

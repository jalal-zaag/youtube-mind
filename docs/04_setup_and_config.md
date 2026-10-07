# 4. Setup & Configuration

## Requirements

- Python 3.10+
- A free Hugging Face token: <https://huggingface.co/settings/tokens> (enable *"Make calls to Inference Providers"*)
- A TranscriptAPI.com key: <https://transcriptapi.com>

## Installation

```bash
cd youtube_mind

# Recommended: use a virtual environment
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env      # then fill in your keys
```

## Environment Variables (`.env`)

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `HUGGINGFACEHUB_API_TOKEN` | ✅ | — | Auth for the remote HF Inference API |
| `YOUTUBE_TRANSCRIPT_API_KEY` | ✅ | — | Auth for TranscriptAPI.com (`sk_...`) |
| `HF_LLM_MODEL` | | `meta-llama/Llama-3.1-8B-Instruct` | Chat model |
| `HF_EMBEDDING_MODEL` | | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `LLM_TEMPERATURE` | | `0.3` | Creativity of responses |
| `LLM_MAX_NEW_TOKENS` | | `1024` | Max length of a summary |
| `QA_TOP_K` | | `5` | Default passages per answer |
| `REQUEST_TIMEOUT` | | `60` | Seconds per API request |

If a required variable is missing, the app shows an error on startup instead of crashing.

## Run

```bash
streamlit run app.py
```

Open <http://localhost:8501>, paste a YouTube URL, and click **Load video**.

## Tests

```bash
python -m pytest -q
```

| Test file | Covers |
|---|---|
| `tests/test_url_parser.py` | All supported URL formats + invalid inputs |
| `tests/test_chunking.py` | Word limits, overlap, empty segments, timestamp formatting |
| `tests/test_vector_store.py` | Ranking order, top-k bounds |
| `tests/test_transcript_service.py` | API response parsing, empty transcript |

Tests make no network calls and use no real API keys.

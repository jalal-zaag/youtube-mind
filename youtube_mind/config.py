"""Application settings loaded from environment variables / .env file."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from youtube_mind.exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return int(value) if value else default


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value else default


@dataclass(frozen=True)
class Settings:
    # Secrets
    hf_token: str
    transcript_api_key: str

    # Remote Hugging Face models (served by the HF Inference API, nothing runs locally)
    llm_model: str
    embedding_model: str

    # Generation
    temperature: float
    max_new_tokens: int

    # Transcript API
    transcript_api_url: str
    request_timeout: int

    # Summarisation (map-reduce) sizing, in words
    single_pass_word_limit: int
    summary_chunk_words: int

    # Retrieval (Q&A) sizing
    qa_chunk_words: int
    qa_chunk_overlap_words: int
    top_k: int

    @classmethod
    def from_env(cls) -> "Settings":
        hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HF_TOKEN", "")
        transcript_key = os.getenv("YOUTUBE_TRANSCRIPT_API_KEY", "")

        missing = [
            name
            for name, value in (
                ("HUGGINGFACEHUB_API_TOKEN", hf_token),
                ("YOUTUBE_TRANSCRIPT_API_KEY", transcript_key),
            )
            if not value
        ]
        if missing:
            raise ConfigurationError(
                f"Missing required environment variable(s): {', '.join(missing)}. "
                "Add them to your .env file (see .env.example)."
            )

        return cls(
            hf_token=hf_token,
            transcript_api_key=transcript_key,
            llm_model=os.getenv("HF_LLM_MODEL", "meta-llama/Llama-3.1-8B-Instruct"),
            embedding_model=os.getenv(
                "HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
            ),
            temperature=_get_float("LLM_TEMPERATURE", 0.3),
            max_new_tokens=_get_int("LLM_MAX_NEW_TOKENS", 1024),
            transcript_api_url=os.getenv(
                "TRANSCRIPT_API_URL", "https://transcriptapi.com/api/v2/youtube/transcript"
            ),
            request_timeout=_get_int("REQUEST_TIMEOUT", 60),
            single_pass_word_limit=_get_int("SINGLE_PASS_WORD_LIMIT", 3000),
            summary_chunk_words=_get_int("SUMMARY_CHUNK_WORDS", 2500),
            qa_chunk_words=_get_int("QA_CHUNK_WORDS", 180),
            qa_chunk_overlap_words=_get_int("QA_CHUNK_OVERLAP_WORDS", 40),
            top_k=_get_int("QA_TOP_K", 5),
        )

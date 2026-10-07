"""Composition root: wires settings -> services -> pipelines in one place."""

from __future__ import annotations

from dataclasses import dataclass

from huggingface_hub import InferenceClient

from youtube_mind.config import Settings
from youtube_mind.pipelines.qa import VideoQA
from youtube_mind.pipelines.summarizer import Summarizer
from youtube_mind.services.embedding_service import EmbeddingService
from youtube_mind.services.llm_service import LLMService
from youtube_mind.services.transcript_service import TranscriptService


@dataclass(frozen=True)
class Container:
    settings: Settings
    transcripts: TranscriptService
    llm: LLMService
    summarizer: Summarizer
    qa: VideoQA


def build_container(settings: Settings | None = None) -> Container:
    settings = settings or Settings.from_env()

    # Remote inference only: every model call is an HTTPS request to Hugging Face.
    hf_client = InferenceClient(token=settings.hf_token, timeout=settings.request_timeout)

    llm = LLMService(
        hf_client,
        model=settings.llm_model,
        temperature=settings.temperature,
        max_new_tokens=settings.max_new_tokens,
    )
    embeddings = EmbeddingService(hf_client, model=settings.embedding_model)

    return Container(
        settings=settings,
        transcripts=TranscriptService(
            settings.transcript_api_key, settings.transcript_api_url, settings.request_timeout
        ),
        llm=llm,
        summarizer=Summarizer(
            llm,
            single_pass_word_limit=settings.single_pass_word_limit,
            chunk_words=settings.summary_chunk_words,
        ),
        qa=VideoQA(
            llm,
            embeddings,
            chunk_words=settings.qa_chunk_words,
            chunk_overlap_words=settings.qa_chunk_overlap_words,
            top_k=settings.top_k,
        ),
    )

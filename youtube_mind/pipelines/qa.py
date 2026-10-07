"""Retrieval-augmented question answering over one video's transcript."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from youtube_mind import prompts
from youtube_mind.models import ChatMessage, RetrievedChunk, Transcript
from youtube_mind.services.embedding_service import EmbeddingService
from youtube_mind.services.llm_service import LLMService
from youtube_mind.services.vector_store import InMemoryVectorStore
from youtube_mind.utils.chunking import chunk_segments
from youtube_mind.utils.timefmt import format_timestamp

# How many previous chat turns to send so follow-up questions have context.
_HISTORY_TURNS = 4


@dataclass
class VideoIndex:
    """Searchable index of one video. Built once, reused for every question."""

    transcript: Transcript
    store: InMemoryVectorStore


@dataclass
class QAResult:
    sources: list[RetrievedChunk]
    answer_stream: Iterator[str]


class VideoQA:
    def __init__(
        self,
        llm: LLMService,
        embeddings: EmbeddingService,
        chunk_words: int = 180,
        chunk_overlap_words: int = 40,
        top_k: int = 5,
    ) -> None:
        self._llm = llm
        self._embeddings = embeddings
        self._chunk_words = chunk_words
        self._chunk_overlap_words = chunk_overlap_words
        self._top_k = top_k

    def build_index(self, transcript: Transcript) -> VideoIndex:
        chunks = chunk_segments(
            transcript.segments, self._chunk_words, self._chunk_overlap_words
        )
        vectors = self._embeddings.embed([c.text for c in chunks])
        return VideoIndex(transcript=transcript, store=InMemoryVectorStore(chunks, vectors))

    def ask(
        self,
        index: VideoIndex,
        question: str,
        history: list[ChatMessage] | None = None,
        language: str = "English",
        top_k: int | None = None,
    ) -> QAResult:
        history = history or []
        # Include the previous user question in the search query so short
        # follow-ups like "why?" or "explain more" still retrieve the right part.
        previous_questions = [m.content for m in history if m.role == "user"][-1:]
        search_query = " ".join([*previous_questions, question])
        query_vector = self._embeddings.embed_one(search_query)
        sources = index.store.search(query_vector, top_k or self._top_k)

        context = "\n\n".join(
            f"[{format_timestamp(r.chunk.start)} - {format_timestamp(r.chunk.end)}] {r.chunk.text}"
            for r in sorted(sources, key=lambda r: r.chunk.start)
        )

        messages = [
            {
                "role": "system",
                "content": prompts.QA_SYSTEM.format(
                    title=index.transcript.metadata.title, language=language
                ),
            }
        ]
        for message in history[-_HISTORY_TURNS * 2 :]:
            messages.append({"role": message.role, "content": message.content})
        messages.append(
            {"role": "user", "content": prompts.QA_USER.format(context=context, question=question)}
        )

        return QAResult(sources=sources, answer_stream=self._llm.stream(messages, 800))

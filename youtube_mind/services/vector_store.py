"""Minimal in-memory vector index (cosine similarity over normalised vectors).

One video produces at most a few hundred chunks, so brute-force numpy search
is instant and avoids running a vector database.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from youtube_mind.models import Chunk, RetrievedChunk


class InMemoryVectorStore:
    def __init__(self, chunks: Sequence[Chunk], embeddings: np.ndarray) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        self._chunks = list(chunks)
        self._embeddings = embeddings

    def __len__(self) -> int:
        return len(self._chunks)

    def search(self, query_embedding: np.ndarray, k: int) -> list[RetrievedChunk]:
        """Return the top-k chunks by cosine similarity, highest first."""
        if not self._chunks:
            return []
        scores = self._embeddings @ query_embedding
        k = min(k, len(self._chunks))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top])]
        return [RetrievedChunk(chunk=self._chunks[i], score=float(scores[i])) for i in top]

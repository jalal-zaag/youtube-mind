"""Sentence embeddings computed remotely by the Hugging Face Inference API."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from huggingface_hub import InferenceClient

from youtube_mind.exceptions import LLMError
from youtube_mind.services.llm_service import describe_hf_error


class EmbeddingService:
    def __init__(self, client: InferenceClient, model: str, batch_size: int = 32) -> None:
        self._client = client
        self._model = model
        self._batch_size = batch_size

    def embed(self, texts: Sequence[str]) -> np.ndarray:
        """Return an (n, dim) array of L2-normalised embeddings."""
        if not texts:
            return np.empty((0, 0), dtype=np.float32)

        batches = []
        for i in range(0, len(texts), self._batch_size):
            batch = list(texts[i : i + self._batch_size])
            try:
                vectors = self._client.feature_extraction(batch, model=self._model)
            except Exception as exc:  # noqa: BLE001
                raise LLMError(describe_hf_error(self._model, exc)) from exc
            batches.append(_to_sentence_vectors(np.asarray(vectors, dtype=np.float32)))

        matrix = np.vstack(batches)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        return matrix / np.clip(norms, 1e-12, None)

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


def _to_sentence_vectors(array: np.ndarray) -> np.ndarray:
    # Sentence-transformer models return (n, dim). Raw transformer models return
    # token-level (n, tokens, dim) features, so mean-pool those.
    if array.ndim == 3:
        return array.mean(axis=1)
    if array.ndim == 1:
        return array[None, :]
    return array

import numpy as np

from youtube_mind.models import Chunk
from youtube_mind.services.vector_store import InMemoryVectorStore


def test_search_returns_most_similar_first():
    chunks = [Chunk(i, f"c{i}", i, i + 1) for i in range(3)]
    vectors = np.eye(3, dtype=np.float32)
    store = InMemoryVectorStore(chunks, vectors)

    results = store.search(np.array([0.1, 0.9, 0.3], dtype=np.float32), k=2)

    assert [r.chunk.index for r in results] == [1, 2]
    assert results[0].score > results[1].score


def test_k_larger_than_store():
    store = InMemoryVectorStore([Chunk(0, "a", 0, 1)], np.ones((1, 2), dtype=np.float32))
    assert len(store.search(np.ones(2, dtype=np.float32), k=10)) == 1

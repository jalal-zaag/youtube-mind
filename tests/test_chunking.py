from youtube_mind.models import TranscriptSegment
from youtube_mind.utils.chunking import chunk_segments
from youtube_mind.utils.timefmt import format_timestamp


def make_segments(n, words_each=10):
    return [
        TranscriptSegment(text=" ".join([f"w{i}"] * words_each), start=i * 5.0, duration=5.0)
        for i in range(n)
    ]


def test_chunks_respect_word_limit_and_cover_all_segments():
    segments = make_segments(20)
    chunks = chunk_segments(segments, max_words=30)
    assert all(len(c.text.split()) <= 30 for c in chunks)
    joined = " ".join(c.text for c in chunks)
    assert all(f"w{i}" in joined for i in range(20))
    assert chunks[0].start == 0.0 and chunks[-1].end == 100.0


def test_overlap_repeats_tail_of_previous_chunk():
    chunks = chunk_segments(make_segments(10), max_words=30, overlap_words=10)
    assert len(chunks) > 1
    for prev, nxt in zip(chunks, chunks[1:]):
        assert prev.text.split()[-1] == nxt.text.split()[0]


def test_no_duplicate_trailing_chunk_when_only_overlap_remains():
    chunks = chunk_segments(make_segments(3), max_words=30, overlap_words=10)
    assert len(chunks) == 1


def test_skips_empty_segments():
    segments = [TranscriptSegment("", 0, 1), TranscriptSegment("hello", 1, 1)]
    chunks = chunk_segments(segments, max_words=10)
    assert [c.text for c in chunks] == ["hello"]


def test_format_timestamp():
    assert format_timestamp(0) == "0:00"
    assert format_timestamp(75.9) == "1:15"
    assert format_timestamp(3725) == "1:02:05"

"""Split transcript segments into word-bounded, time-aware chunks."""

from __future__ import annotations

from collections.abc import Sequence

from youtube_mind.models import Chunk, TranscriptSegment


def chunk_segments(
    segments: Sequence[TranscriptSegment],
    max_words: int,
    overlap_words: int = 0,
) -> list[Chunk]:
    """Group consecutive segments into chunks of roughly `max_words` words.

    Segments are never split, so each chunk keeps accurate start/end times.
    The last segments of a chunk (up to `overlap_words` words) are repeated at
    the start of the next one so answers spanning a boundary are not lost.
    """
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if not 0 <= overlap_words < max_words:
        raise ValueError("overlap_words must be in [0, max_words)")

    chunks: list[Chunk] = []
    window: list[TranscriptSegment] = []
    window_words = 0
    new_in_window = 0  # segments added since the last emitted chunk

    def emit() -> None:
        chunks.append(
            Chunk(
                index=len(chunks),
                text=" ".join(s.text for s in window),
                start=window[0].start,
                end=window[-1].end,
            )
        )

    for segment in segments:
        text = " ".join(segment.text.split())
        if not text:
            continue
        segment = TranscriptSegment(text=text, start=segment.start, duration=segment.duration)
        words = len(text.split())

        if window and window_words + words > max_words:
            emit()
            # Keep a tail of the window as overlap for the next chunk.
            tail: list[TranscriptSegment] = []
            tail_words = 0
            for prev in reversed(window):
                prev_words = len(prev.text.split())
                if tail_words + prev_words > overlap_words:
                    break
                tail.insert(0, prev)
                tail_words += prev_words
            window, window_words, new_in_window = tail, tail_words, 0

        window.append(segment)
        window_words += words
        new_in_window += 1

    if window and new_in_window:
        emit()
    return chunks

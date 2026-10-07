"""Plain data objects shared across layers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TranscriptSegment:
    text: str
    start: float
    duration: float

    @property
    def end(self) -> float:
        return self.start + self.duration


@dataclass(frozen=True)
class VideoMetadata:
    video_id: str
    title: str
    author: str = ""
    author_url: str = ""
    thumbnail_url: str = ""
    length_seconds: int | None = None
    language: str = ""

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


@dataclass(frozen=True)
class Transcript:
    metadata: VideoMetadata
    segments: tuple[TranscriptSegment, ...]

    @property
    def full_text(self) -> str:
        return " ".join(s.text for s in self.segments)

    @property
    def word_count(self) -> int:
        return len(self.full_text.split())


@dataclass(frozen=True)
class Chunk:
    """A contiguous window of transcript text with its time span."""

    index: int
    text: str
    start: float
    end: float


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float


@dataclass
class ChatMessage:
    role: str  # "user" | "assistant"
    content: str
    sources: list[RetrievedChunk] = field(default_factory=list)

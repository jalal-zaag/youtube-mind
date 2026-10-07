import pytest

from youtube_mind.exceptions import TranscriptError
from youtube_mind.services.transcript_service import TranscriptService


def test_parse_payload():
    payload = {
        "video_id": "abcdefghijk",
        "language": "en",
        "length_seconds": 120,
        "metadata": {"title": "My Video", "author_name": "Me"},
        "transcript": [
            {"text": "hello\nworld", "start": 0.0, "duration": 2.0},
            {"text": "   ", "start": 2.0, "duration": 1.0},
            {"text": "bye", "start": 3.0, "duration": 1.5},
        ],
    }
    t = TranscriptService._parse("abcdefghijk", payload)
    assert t.metadata.title == "My Video"
    assert [s.text for s in t.segments] == ["hello world", "bye"]
    assert t.word_count == 3


def test_empty_transcript_raises():
    with pytest.raises(TranscriptError):
        TranscriptService._parse("x", {"transcript": []})

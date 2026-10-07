"""Timestamp helpers."""

from __future__ import annotations


def format_timestamp(seconds: float) -> str:
    """Format seconds as `M:SS` or `H:MM:SS`."""
    total = max(0, int(seconds))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def timestamp_url(video_id: str, seconds: float) -> str:
    """Deep link that opens the video at the given second."""
    return f"https://youtu.be/{video_id}?t={max(0, int(seconds))}"

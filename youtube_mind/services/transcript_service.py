"""Fetch YouTube transcripts + metadata from TranscriptAPI.com."""

from __future__ import annotations

from typing import Any

import requests

from youtube_mind.exceptions import TranscriptError
from youtube_mind.models import Transcript, TranscriptSegment, VideoMetadata

_STATUS_MESSAGES = {
    400: "The video URL was rejected by the transcript service.",
    401: "YOUTUBE_TRANSCRIPT_API_KEY is invalid or expired.",
    402: "Your transcript API credits are used up.",
    403: "Access to this video's transcript is forbidden (private or restricted video?).",
    404: "No transcript is available for this video (captions may be disabled).",
    429: "Transcript API rate limit reached. Please wait a moment and try again.",
}


class TranscriptService:
    def __init__(self, api_key: str, api_url: str, timeout: int = 60) -> None:
        self._api_url = api_url
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": f"Bearer {api_key}"})

    def fetch(self, video_id: str) -> Transcript:
        try:
            response = self._session.get(
                self._api_url,
                params={
                    "video_url": video_id,
                    "format": "json",
                    "include_timestamp": "true",
                    "send_metadata": "true",
                },
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            raise TranscriptError(f"Could not reach the transcript service: {exc}") from exc

        if response.status_code != 200:
            message = _STATUS_MESSAGES.get(
                response.status_code,
                f"Transcript service returned HTTP {response.status_code}.",
            )
            raise TranscriptError(message)

        try:
            return self._parse(video_id, response.json())
        except (ValueError, KeyError, TypeError) as exc:
            raise TranscriptError("Unexpected response from the transcript service.") from exc

    @staticmethod
    def _parse(video_id: str, payload: dict[str, Any]) -> Transcript:
        segments = tuple(
            TranscriptSegment(
                text=str(item.get("text", "")).replace("\n", " ").strip(),
                start=float(item.get("start", 0.0)),
                duration=float(item.get("duration", 0.0)),
            )
            for item in payload["transcript"]
            if str(item.get("text", "")).strip()
        )
        if not segments:
            raise TranscriptError("The transcript for this video is empty.")

        meta = payload.get("metadata") or {}
        metadata = VideoMetadata(
            video_id=payload.get("video_id", video_id),
            title=meta.get("title") or video_id,
            author=meta.get("author_name", ""),
            author_url=meta.get("author_url", ""),
            thumbnail_url=meta.get("thumbnail_url", ""),
            length_seconds=payload.get("length_seconds") or int(segments[-1].end),
            language=payload.get("language", ""),
        )
        return Transcript(metadata=metadata, segments=segments)

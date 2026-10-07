"""Extract a YouTube video ID from the many URL shapes users paste."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

from youtube_mind.exceptions import InvalidURLError

_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
_YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtube-nocookie.com",
    "www.youtube-nocookie.com",
}
_PATH_PREFIXES = ("/shorts/", "/embed/", "/live/", "/v/", "/e/")


def extract_video_id(url_or_id: str) -> str:
    """Return the 11-character video ID or raise `InvalidURLError`.

    Supports watch URLs, youtu.be short links, /shorts/, /embed/, /live/,
    mobile and music hosts, and a bare video ID.
    """
    text = (url_or_id or "").strip()
    if not text:
        raise InvalidURLError("Please paste a YouTube video URL.")

    if _VIDEO_ID_RE.match(text):
        return text

    if "://" not in text:
        text = "https://" + text
    parsed = urlparse(text)
    host = (parsed.hostname or "").lower()

    candidate = None
    if host == "youtu.be":
        candidate = parsed.path.lstrip("/").split("/")[0]
    elif host in _YOUTUBE_HOSTS:
        if parsed.path == "/watch":
            candidate = parse_qs(parsed.query).get("v", [None])[0]
        else:
            for prefix in _PATH_PREFIXES:
                if parsed.path.startswith(prefix):
                    candidate = parsed.path[len(prefix):].split("/")[0]
                    break

    if candidate and _VIDEO_ID_RE.match(candidate):
        return candidate
    raise InvalidURLError(f"Could not find a YouTube video ID in: {url_or_id!r}")

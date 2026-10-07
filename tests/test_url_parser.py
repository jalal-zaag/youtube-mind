import pytest

from youtube_mind.exceptions import InvalidURLError
from youtube_mind.utils.url_parser import extract_video_id

VID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "url",
    [
        VID,
        f"https://www.youtube.com/watch?v={VID}",
        f"https://youtube.com/watch?v={VID}&t=42s&list=PL123",
        f"youtube.com/watch?v={VID}",
        f"https://m.youtube.com/watch?v={VID}",
        f"https://music.youtube.com/watch?v={VID}",
        f"https://youtu.be/{VID}",
        f"https://youtu.be/{VID}?si=abc&t=10",
        f"https://www.youtube.com/shorts/{VID}",
        f"https://www.youtube.com/embed/{VID}",
        f"https://www.youtube.com/live/{VID}?feature=share",
        f"  https://www.youtube.com/watch?v={VID}  ",
    ],
)
def test_extracts_id(url):
    assert extract_video_id(url) == VID


@pytest.mark.parametrize(
    "url",
    ["", "   ", "https://vimeo.com/123", "https://www.youtube.com/watch?v=short", "hello world",
     "https://www.youtube.com/@channel"],
)
def test_rejects_invalid(url):
    with pytest.raises(InvalidURLError):
        extract_video_id(url)

"""Typed accessors for Streamlit session state."""

from __future__ import annotations

from dataclasses import dataclass, field

import streamlit as st

from youtube_mind.models import ChatMessage, Transcript
from youtube_mind.pipelines.qa import VideoIndex

_KEY = "youtube_mind_state"


@dataclass
class AppState:
    transcript: Transcript | None = None
    index: VideoIndex | None = None  # built lazily on the first question
    summary: str = ""
    summary_style: str = ""
    messages: list[ChatMessage] = field(default_factory=list)

    def load_video(self, transcript: Transcript) -> None:
        """Switch to a new video and drop everything derived from the old one."""
        self.transcript = transcript
        self.index = None
        self.summary = ""
        self.summary_style = ""
        self.messages = []


def get_state() -> AppState:
    if _KEY not in st.session_state:
        st.session_state[_KEY] = AppState()
    return st.session_state[_KEY]

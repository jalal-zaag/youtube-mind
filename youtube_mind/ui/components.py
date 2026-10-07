"""Reusable Streamlit view components (presentation only, no business logic)."""

from __future__ import annotations

import streamlit as st

from youtube_mind.models import RetrievedChunk, Transcript
from youtube_mind.utils.timefmt import format_timestamp, timestamp_url

CUSTOM_CSS = """
<style>
.block-container {padding-top: 2rem; max-width: 1100px;}
.ym-hero h1 {margin-bottom: 0;}
.ym-hero p {color: #888; margin-top: .25rem;}
.ym-meta {font-size: .95rem; line-height: 1.7;}
.ym-meta b {font-weight: 600;}
</style>
"""


def render_header() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div class="ym-hero"><h1>🧠 YouTube Mind</h1>'
        "<p>Paste a YouTube link, get a summary, and ask the video anything.</p></div>",
        unsafe_allow_html=True,
    )


def render_video_card(transcript: Transcript) -> None:
    meta = transcript.metadata
    col_video, col_info = st.columns([3, 2], gap="large")
    with col_video:
        st.video(meta.url)
    with col_info:
        st.subheader(meta.title)
        rows = []
        if meta.author:
            channel = f"[{meta.author}]({meta.author_url})" if meta.author_url else meta.author
            rows.append(f"**Channel:** {channel}")
        if meta.length_seconds:
            rows.append(f"**Duration:** {format_timestamp(meta.length_seconds)}")
        if meta.language:
            rows.append(f"**Transcript language:** `{meta.language}`")
        rows.append(f"**Transcript length:** {transcript.word_count:,} words")
        st.markdown("  \n".join(rows))


def render_sources(video_id: str, sources: list[RetrievedChunk]) -> None:
    if not sources:
        return
    with st.expander(f"📍 Sources from the video ({len(sources)})"):
        for source in sorted(sources, key=lambda s: s.chunk.start):
            chunk = source.chunk
            link = timestamp_url(video_id, chunk.start)
            st.markdown(
                f"**[{format_timestamp(chunk.start)} - {format_timestamp(chunk.end)}]({link})**"
                f" &nbsp;·&nbsp; relevance {source.score:.2f}"
            )
            st.caption(chunk.text)


def render_transcript(transcript: Transcript) -> None:
    video_id = transcript.metadata.video_id
    query = st.text_input("Search transcript", placeholder="Filter lines by keyword...")
    lines = []
    for seg in transcript.segments:
        if query and query.lower() not in seg.text.lower():
            continue
        lines.append(
            f"[`{format_timestamp(seg.start)}`]({timestamp_url(video_id, seg.start)}) {seg.text}"
        )
    with st.container(height=480):
        st.markdown("  \n".join(lines) if lines else "_No matching lines._")
    st.download_button(
        "⬇️ Download transcript (.txt)",
        data="\n".join(f"[{format_timestamp(s.start)}] {s.text}" for s in transcript.segments),
        file_name=f"{video_id}_transcript.txt",
        mime="text/plain",
    )

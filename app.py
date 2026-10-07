"""YouTube Mind - Streamlit entry point.

Run with:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from youtube_mind.container import Container, build_container
from youtube_mind.exceptions import YouTubeMindError
from youtube_mind.models import ChatMessage, Transcript
from youtube_mind.prompts import SUMMARY_STYLES
from youtube_mind.ui import components
from youtube_mind.ui.state import AppState, get_state
from youtube_mind.utils.url_parser import extract_video_id

LANGUAGES = ["English", "Bengali", "Hindi", "Spanish", "French", "German", "Arabic", "Urdu"]
VIEWS = ["📝 Summary", "💬 Ask the video", "📜 Transcript"]

st.set_page_config(page_title="YouTube Mind", page_icon="🧠", layout="wide")


@st.cache_resource(show_spinner=False)
def get_container() -> Container:
    return build_container()


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24, max_entries=50)
def fetch_transcript(video_id: str) -> Transcript:
    # Cached per video so re-loading a video doesn't spend API credits.
    return get_container().transcripts.fetch(video_id)


def render_sidebar(container: Container) -> dict:
    with st.sidebar:
        st.header("⚙️ Settings")
        style = st.selectbox("Summary style", list(SUMMARY_STYLES), index=1)
        # language = st.selectbox("Response language", LANGUAGES, index=0)
        language = "English"  # responses are always in English for now
        top_k = st.slider(
            "Transcript passages per answer",
            min_value=2,
            max_value=10,
            value=container.settings.top_k,
            help="How many relevant transcript passages are given to the model per question.",
        )
        st.divider()
        st.caption("**Remote models (Hugging Face Inference API)**")
        st.caption(f"LLM: `{container.settings.llm_model}`")
        st.caption(f"Embeddings: `{container.settings.embedding_model}`")
    return {"style": style, "language": language, "top_k": top_k}


def render_url_form(state: AppState) -> None:
    with st.form("url_form", border=False):
        col_input, col_button = st.columns([5, 1], vertical_alignment="bottom")
        url = col_input.text_input(
            "YouTube URL",
            placeholder="https://www.youtube.com/watch?v=...",
            label_visibility="collapsed",
        )
        submitted = col_button.form_submit_button(
            "Load video", type="primary", use_container_width=True
        )

    if not submitted:
        return
    try:
        video_id = extract_video_id(url)
        with st.spinner("Fetching transcript..."):
            transcript = fetch_transcript(video_id)
        state.load_video(transcript)
    except YouTubeMindError as err:
        st.error(str(err))


def render_summary_view(container: Container, state: AppState, options: dict) -> None:
    transcript = state.transcript
    label = "Regenerate summary" if state.summary else "Generate summary"
    if st.button(f"✨ {label}", type="primary"):
        status = st.status("Summarising...", expanded=False)
        progress = status.progress(0.0)

        def on_progress(value: float, message: str) -> None:
            progress.progress(value, text=message)

        try:
            stream = container.summarizer.summarize(
                transcript, style=options["style"], language=options["language"],
                on_progress=on_progress,
            )
            state.summary = st.write_stream(stream)
            state.summary_style = options["style"]
        except YouTubeMindError as err:
            status.update(label="Summarisation failed", state="error")
            st.error(str(err))
            return
        st.rerun()  # re-render with the stored summary + download button

    if state.summary:
        st.caption(f"Style: {state.summary_style}")
        st.markdown(state.summary)
        st.download_button(
            "⬇️ Download summary (.md)",
            data=f"# {transcript.metadata.title}\n\n{transcript.metadata.url}\n\n{state.summary}",
            file_name=f"{transcript.metadata.video_id}_summary.md",
            mime="text/markdown",
        )
    else:
        st.info("Click **Generate summary** to summarise this video.")


def render_chat_view(container: Container, state: AppState, options: dict) -> None:
    video_id = state.transcript.metadata.video_id

    if state.messages and st.sidebar.button("🗑️ Clear chat", use_container_width=True):
        state.messages = []
        st.rerun()

    if not state.messages:
        st.info("Ask anything about the video, e.g. *“What are the main arguments?”*")
    for message in state.messages:
        with st.chat_message(message.role):
            st.markdown(message.content)
            components.render_sources(video_id, message.sources)

    question = st.chat_input("Ask a question about this video...")
    if not question:
        return

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            if state.index is None:
                with st.spinner("Indexing the transcript (one-time per video)..."):
                    state.index = container.qa.build_index(state.transcript)
            result = container.qa.ask(
                state.index,
                question,
                history=state.messages,
                language=options["language"],
                top_k=options["top_k"],
            )
            answer = st.write_stream(result.answer_stream)
            components.render_sources(video_id, result.sources)
        except YouTubeMindError as err:
            st.error(str(err))
            return

    state.messages.append(ChatMessage(role="user", content=question))
    state.messages.append(ChatMessage(role="assistant", content=answer, sources=result.sources))


def main() -> None:
    components.render_header()
    try:
        container = get_container()
    except YouTubeMindError as err:
        st.error(str(err))
        st.stop()

    state = get_state()
    options = render_sidebar(container)
    render_url_form(state)

    if state.transcript is None:
        st.caption("Works with watch links, youtu.be links, Shorts, and live replays.")
        return

    components.render_video_card(state.transcript)
    st.divider()

    view = st.segmented_control(
        "View", VIEWS, default=VIEWS[0], key="view", label_visibility="collapsed"
    )
    if view == VIEWS[1]:
        render_chat_view(container, state, options)
    elif view == VIEWS[2]:
        components.render_transcript(state.transcript)
    else:
        render_summary_view(container, state, options)


if __name__ == "__main__":
    main()

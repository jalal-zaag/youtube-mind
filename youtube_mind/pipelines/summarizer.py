"""Map-reduce summarisation so videos of any length fit in the model context."""

from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence

from youtube_mind import prompts
from youtube_mind.models import Transcript, TranscriptSegment
from youtube_mind.services.llm_service import LLMService
from youtube_mind.utils.timefmt import format_timestamp

ProgressCallback = Callable[[float, str], None]


class Summarizer:
    def __init__(
        self,
        llm: LLMService,
        single_pass_word_limit: int = 3000,
        chunk_words: int = 2500,
    ) -> None:
        self._llm = llm
        self._single_pass_word_limit = single_pass_word_limit
        self._chunk_words = chunk_words

    def summarize(
        self,
        transcript: Transcript,
        style: str = "Detailed",
        language: str = "English",
        on_progress: ProgressCallback | None = None,
    ) -> Iterator[str]:
        """Stream the final summary.

        Short videos are summarised in one call. Long videos are split into
        chunks, each chunk is condensed to notes (map), and the notes are
        merged into the final summary (reduce).
        """
        progress = on_progress or (lambda _p, _m: None)
        title = transcript.metadata.title

        if transcript.word_count <= self._single_pass_word_limit:
            source_label = "Transcript (each line starts with its [M:SS] timestamp)"
            source_text = _timestamped_text(transcript.segments)
        else:
            groups = _group_segments(transcript.segments, self._chunk_words)
            notes = []
            for i, group in enumerate(groups, start=1):
                progress((i - 1) / len(groups), f"Reading part {i} of {len(groups)}...")
                notes.append(self._map_part(group, i, len(groups), title))
            source_label = "Notes taken from consecutive parts of the video"
            source_text = "\n\n".join(notes)

        progress(1.0, "Writing summary...")
        style_instructions = prompts.SUMMARY_STYLES.get(style, prompts.SUMMARY_STYLES["Detailed"])
        messages = [
            {"role": "system", "content": prompts.SUMMARY_SYSTEM},
            {
                "role": "user",
                "content": prompts.REDUCE_PROMPT.format(
                    title=title,
                    source_label=source_label,
                    text=source_text,
                    style_instructions=style_instructions,
                    language=language,
                ),
            },
        ]
        yield from self._llm.stream(messages)

    def _map_part(
        self, segments: list[TranscriptSegment], part: int, total: int, title: str
    ) -> str:
        messages = [
            {"role": "system", "content": prompts.SUMMARY_SYSTEM},
            {
                "role": "user",
                "content": prompts.MAP_PROMPT.format(
                    part=part, total=total, title=title, text=_timestamped_text(segments)
                ),
            },
        ]
        return self._llm.complete(messages, max_new_tokens=600)


def _group_segments(
    segments: Sequence[TranscriptSegment], max_words: int
) -> list[list[TranscriptSegment]]:
    """Split segments into consecutive groups of at most ~`max_words` words."""
    groups: list[list[TranscriptSegment]] = [[]]
    words = 0
    for seg in segments:
        seg_words = len(seg.text.split())
        if groups[-1] and words + seg_words > max_words:
            groups.append([])
            words = 0
        groups[-1].append(seg)
        words += seg_words
    return [g for g in groups if g]


def _timestamped_text(segments: Sequence[TranscriptSegment]) -> str:
    """Render segments as `[M:SS] text` lines, merging them into ~30 second lines."""
    lines: list[str] = []
    line_start: float | None = None
    buffer: list[str] = []
    for seg in segments:
        if line_start is None:
            line_start = seg.start
        buffer.append(seg.text)
        if seg.end - line_start >= 30:
            lines.append(f"[{format_timestamp(line_start)}] {' '.join(buffer)}")
            line_start, buffer = None, []
    if buffer and line_start is not None:
        lines.append(f"[{format_timestamp(line_start)}] {' '.join(buffer)}")
    return "\n".join(lines)

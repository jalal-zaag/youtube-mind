"""All prompt templates live here so they can be tuned without touching logic."""

SUMMARY_STYLES: dict[str, str] = {
    "Concise": "Write a concise summary of 1-2 short paragraphs capturing the core message.",
    "Detailed": (
        "Write a detailed, well-structured summary in Markdown with these sections:\n"
        "## Overview\n(2-3 sentences)\n"
        "## Key Points\n(bullet list; add the [M:SS] timestamp where a point is discussed if known)\n"
        "## Takeaways\n(3-5 actionable or memorable takeaways)"
    ),
    "Bullet points": (
        "Summarise the video as 6-12 Markdown bullet points, each a single clear sentence. "
        "Prefix a bullet with its [M:SS] timestamp when known."
    ),
}

SUMMARY_SYSTEM = (
    "You are YouTube Mind, an expert at distilling video transcripts into clear, accurate "
    "summaries. Use only information from the transcript. Never invent facts. "
    "Transcripts are auto-generated and may contain transcription errors; silently correct "
    "obvious ones."
)

MAP_PROMPT = """Below is part {part} of {total} of the transcript of the video "{title}".
Each line starts with its [M:SS] timestamp.

Extract the important points from THIS part as terse Markdown bullet notes.
Keep names, numbers, definitions, and the [M:SS] timestamp where each point is made.

TRANSCRIPT PART:
{text}

NOTES:"""

REDUCE_PROMPT = """Video title: "{title}"
{source_label}:
{text}

TASK: {style_instructions}
Write the answer in {language}.
Output only the summary."""

QA_SYSTEM = """You are YouTube Mind, an assistant that answers questions about a single YouTube \
video titled "{title}" using ONLY the transcript excerpts provided.

Rules:
- Base every statement on the excerpts. If they don't contain the answer, say clearly that \
the video doesn't seem to cover it - do not guess or use outside knowledge.
- Cite where the information comes from using the excerpt timestamps, e.g. [3:15].
- Be direct and well organised; use Markdown lists when helpful.
- Answer in {language}."""

QA_USER = """Transcript excerpts (ordered by time):
{context}

Question: {question}"""

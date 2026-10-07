"""Domain exceptions. The UI catches `YouTubeMindError` and shows `str(err)` to the user."""


class YouTubeMindError(Exception):
    """Base class for all expected, user-presentable errors."""


class ConfigurationError(YouTubeMindError):
    """Required configuration (API keys, etc.) is missing or invalid."""


class InvalidURLError(YouTubeMindError):
    """The given text is not a recognisable YouTube video URL or ID."""


class TranscriptError(YouTubeMindError):
    """The transcript could not be fetched."""


class LLMError(YouTubeMindError):
    """The remote language / embedding model call failed."""

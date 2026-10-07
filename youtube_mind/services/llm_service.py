"""Chat model served remotely by the Hugging Face Inference API."""

from __future__ import annotations

import time
from collections.abc import Iterator

from huggingface_hub import InferenceClient

from youtube_mind.exceptions import LLMError

Message = dict[str, str]


class LLMService:
    """Thin wrapper around `InferenceClient.chat_completion` with retries."""

    def __init__(
        self,
        client: InferenceClient,
        model: str,
        temperature: float = 0.3,
        max_new_tokens: int = 1024,
        max_retries: int = 2,
    ) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature
        self._max_new_tokens = max_new_tokens
        self._max_retries = max_retries

    @property
    def model(self) -> str:
        return self._model

    def complete(self, messages: list[Message], max_new_tokens: int | None = None) -> str:
        """Return the full completion text."""
        response = self._with_retries(
            lambda: self._client.chat_completion(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=max_new_tokens or self._max_new_tokens,
            )
        )
        return (response.choices[0].message.content or "").strip()

    def stream(self, messages: list[Message], max_new_tokens: int | None = None) -> Iterator[str]:
        """Yield the completion token by token (for live UI rendering)."""
        stream = self._with_retries(
            lambda: self._client.chat_completion(
                model=self._model,
                messages=messages,
                temperature=self._temperature,
                max_tokens=max_new_tokens or self._max_new_tokens,
                stream=True,
            )
        )
        try:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as exc:  # noqa: BLE001 - surface any streaming failure uniformly
            raise LLMError(f"The model stream was interrupted: {exc}") from exc

    def _with_retries(self, call):
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return call()
            except Exception as exc:  # noqa: BLE001 - HF raises several error types
                last_exc = exc
                if attempt < self._max_retries and _is_retryable(exc):
                    time.sleep(2 ** attempt)
                    continue
                break
        raise LLMError(describe_hf_error(self._model, last_exc)) from last_exc


_HF_STATUS_MESSAGES = {
    401: "Your HUGGINGFACEHUB_API_TOKEN is invalid. Create a new one at "
    "https://huggingface.co/settings/tokens.",
    402: "Your free Hugging Face Inference credits for this month are used up. "
    "Wait for the monthly reset, use another HF token, or add credits at "
    "https://huggingface.co/settings/billing.",
    403: "Your Hugging Face token lacks permission for this model. Enable "
    "'Make calls to Inference Providers' on the token.",
    404: "Model not found on Hugging Face Inference. Check the model name in .env.",
    429: "Hugging Face rate limit reached. Please wait a minute and try again.",
}


def _status_code(exc: Exception | None) -> int | None:
    return getattr(getattr(exc, "response", None), "status_code", None)


def describe_hf_error(model: str, exc: Exception | None) -> str:
    """Turn a Hugging Face client exception into a user-facing message."""
    status = _status_code(exc)
    if status in _HF_STATUS_MESSAGES:
        return _HF_STATUS_MESSAGES[status]
    if status == 400 and "not supported" in str(exc):
        return f"Model '{model}' is not served by any Inference Provider. Pick another model."
    return f"Hugging Face model '{model}' failed: {exc}"


def _is_retryable(exc: Exception) -> bool:
    return _status_code(exc) in {429, 500, 502, 503, 504} or isinstance(
        exc, (TimeoutError, ConnectionError)
    )

import time
from typing import Iterator
from groq import Groq
from config.settings import settings
from providers.base import BaseProvider, LLMResponse


class GroqProvider(BaseProvider):

    def __init__(self, model_id: str):
        self.model_id = model_id
        self._client = Groq(api_key=settings.groq_api_key)

    def call(self, prompt: str, system: str = "", max_tokens: int = 1024) -> LLMResponse:
        start = time.time()

        response = self._client.chat.completions.create(
            model=self.model_id,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system or "You are a helpful assistant."},
                {"role": "user",   "content": prompt},
            ],
        )

        latency_ms = int((time.time() - start) * 1000)
        choice = response.choices[0]

        return LLMResponse(
            content=choice.message.content,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            latency_ms=latency_ms,
            model_id=self.model_id,
            provider="groq",
        )

    def stream(self, prompt: str, system: str = "", max_tokens: int = 1024) -> Iterator[str]:
        response = self._client.chat.completions.create(
            model=self.model_id,
            max_tokens=max_tokens,
            stream=True,
            messages=[
                {"role": "system", "content": system or "You are a helpful assistant."},
                {"role": "user",   "content": prompt},
            ],
        )

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    def is_available(self) -> bool:
        return bool(settings.groq_api_key)
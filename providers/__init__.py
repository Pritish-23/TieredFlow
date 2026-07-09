from config.constants import MODELS, Tier
from providers.anthropic_provider import AnthropicProvider
from providers.base import BaseProvider
from providers.groq_provider import GroqProvider
from providers.openai_provider import OpenAIProvider


def get_provider(tier: Tier) -> BaseProvider:
    meta = MODELS[tier]
    match meta.provider:
        case "anthropic":
            return AnthropicProvider(model_id=meta.model_id)
        case "openai":
            return OpenAIProvider(model_id=meta.model_id)
        case "groq":
            return GroqProvider(model_id=meta.model_id)
        case _:
            raise ValueError(f"Unknown provider: {meta.provider}")

"""
LLM Provider implementations for autonomous computer control.

Supports multiple providers with vision and computer use capabilities.
"""

from .base import (
    BaseLLMProvider,
    ProviderError,
    ProviderAPIError,
    ProviderNotAvailableError,
    ProviderInfo,
    ProviderResponse,
    ProviderType,
)

# Conditional imports to avoid missing dependency errors
try:
    from .anthropic_provider import AnthropicProvider
except ImportError:
    AnthropicProvider = None

try:
    from .gemini_provider import GeminiProvider
except ImportError:
    GeminiProvider = None

try:
    from .openai_provider import OpenAIProvider
except ImportError:
    OpenAIProvider = None

try:
    from .featherless_provider import FeatherlessProvider
except ImportError:
    FeatherlessProvider = None

from .factory import ProviderFactory, get_available_providers, create_provider

__all__ = [
    "BaseLLMProvider",
    "ProviderError",
    "ProviderAPIError",
    "ProviderNotAvailableError",
    "ProviderInfo",
    "ProviderResponse",
    "ProviderType",
    "AnthropicProvider",
    "GeminiProvider",
    "OpenAIProvider",
    "FeatherlessProvider",
    "ProviderFactory",
    "get_available_providers",
    "create_provider",
]

"""
Provider factory for auto-selecting and managing LLM providers.

Implements fallback chain: Gemini Free → Claude → OpenAI → Featherless
"""

import os
from typing import Dict, List, Optional, Type

from .base import BaseLLMProvider, ProviderInfo, ProviderNotAvailableError, ProviderType
from .anthropic_provider import AnthropicProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .featherless_provider import FeatherlessProvider


# Provider registry
PROVIDER_REGISTRY: Dict[ProviderType, Type[BaseLLMProvider]] = {
    ProviderType.ANTHROPIC: AnthropicProvider,
    ProviderType.GEMINI: GeminiProvider,
    ProviderType.OPENAI: OpenAIProvider,
    ProviderType.FEATHERLESS: FeatherlessProvider,
}


# Default priority order (cost-effective first)
DEFAULT_PRIORITY = [
    ProviderType.GEMINI,      # Free tier - best for cost
    ProviderType.ANTHROPIC,   # User subscription - best for computer use
    ProviderType.OPENAI,      # User subscription - good vision support
    ProviderType.FEATHERLESS, # Cheap alternative
]


class ProviderFactory:
    """
    Factory for creating and managing LLM providers.
    
    Handles auto-selection based on:
    - API key availability
    - Cost-effectiveness (free tier first)
    - Provider capabilities (vision, computer use)
    """
    
    @staticmethod
    def get_available_providers() -> List[ProviderInfo]:
        """
        Get list of available providers (with API keys set).
        
        Returns:
            List of ProviderInfo for available providers.
        """
        available = []
        
        for provider_type, provider_class in PROVIDER_REGISTRY.items():
            if provider_class.is_available():
                available.append(provider_class.get_info())
        
        return available
    
    @staticmethod
    def create_provider(
        provider_type: Optional[ProviderType] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Create a provider instance.
        
        Args:
            provider_type: Type of provider to create. If None, auto-selects.
            api_key: API key for the provider. If None, uses environment.
            model: Model to use. If None, uses provider default.
            
        Returns:
            Configured provider instance.
            
        Raises:
            ProviderNotAvailableError: If provider not available.
        """
        if provider_type is None:
            provider_type = ProviderFactory._auto_select_provider()
        
        provider_class = PROVIDER_REGISTRY.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        return provider_class(api_key=api_key, model=model)
    
    @staticmethod
    def _auto_select_provider() -> ProviderType:
        """
        Auto-select the best available provider.
        
        Priority order:
        1. Gemini (free tier)
        2. Anthropic (best for computer use)
        3. OpenAI (good vision support)
        4. Featherless (cheap alternative)
        
        Returns:
            Selected provider type.
            
        Raises:
            ProviderNotAvailableError: If no providers available.
        """
        # Check environment variable override
        env_provider = os.environ.get("LLM_PROVIDER", "").lower()
        if env_provider and env_provider != "auto":
            # Try to use specified provider
            for provider_type in ProviderType:
                if provider_type.value == env_provider:
                    provider_class = PROVIDER_REGISTRY[provider_type]
                    if provider_class.is_available():
                        return provider_type
                    else:
                        raise ProviderNotAvailableError(
                            f"Specified provider '{env_provider}' not available. "
                            f"Set {provider_type.value.upper()}_API_KEY environment variable."
                        )
        
        # Auto-select based on priority
        for provider_type in DEFAULT_PRIORITY:
            provider_class = PROVIDER_REGISTRY[provider_type]
            if provider_class.is_available():
                return provider_type
        
        # No providers available
        raise ProviderNotAvailableError(
            "No LLM providers available. Please set at least one API key:\n"
            "  - GOOGLE_API_KEY (free tier available)\n"
            "  - ANTHROPIC_API_KEY (best for computer use)\n"
            "  - OPENAI_API_KEY (if you have ChatGPT subscription)\n"
            "  - FEATHERLESS_API_KEY (cheap alternative)"
        )
    
    @staticmethod
    def create_with_fallback(
        preferred_provider: Optional[ProviderType] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """
        Create provider with automatic fallback on failure.
        
        Args:
            preferred_provider: Preferred provider type.
            api_key: API key for the provider.
            model: Model to use.
            
        Returns:
            Configured provider instance.
        """
        # Try preferred provider first
        if preferred_provider:
            try:
                return ProviderFactory.create_provider(
                    provider_type=preferred_provider,
                    api_key=api_key,
                    model=model
                )
            except ProviderNotAvailableError:
                pass  # Fall through to auto-select
        
        # Auto-select if preferred failed or not specified
        return ProviderFactory.create_provider(
            provider_type=None,  # Auto-select
            api_key=api_key,
            model=model
        )


def get_available_providers() -> List[ProviderInfo]:
    """
    Convenience function to get available providers.
    
    Returns:
        List of ProviderInfo for available providers.
    """
    return ProviderFactory.get_available_providers()


def create_provider(
    provider_type: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> BaseLLMProvider:
    """
    Convenience function to create a provider.
    
    Args:
        provider_type: Type of provider ("anthropic", "gemini", "openai", "featherless").
                      If None or "auto", auto-selects.
        api_key: API key for the provider.
        model: Model to use.
        
    Returns:
        Configured provider instance.
    """
    # Convert string to ProviderType
    ptype = None
    if provider_type and provider_type.lower() != "auto":
        for pt in ProviderType:
            if pt.value == provider_type.lower():
                ptype = pt
                break
    
    return ProviderFactory.create_provider(
        provider_type=ptype,
        api_key=api_key,
        model=model
    )

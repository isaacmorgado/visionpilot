"""
Base provider interface for LLM providers.

Defines the abstract interface that all LLM providers must implement
to support computer control with vision capabilities.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ProviderType(str, Enum):
    """Available LLM providers."""
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OPENAI = "openai"
    FEATHERLESS = "featherless"


@dataclass
class ProviderInfo:
    """Information about a provider."""
    name: str
    type: ProviderType
    supports_vision: bool
    supports_computer_use: bool
    cost_per_1m_tokens: float
    free_tier: bool
    description: str


@dataclass
class ProviderMessage:
    """A message in provider format."""
    role: str  # "user" or "assistant"
    content: Any  # Can be string or list of content blocks


@dataclass
class ProviderResponse:
    """Standardized response from any provider."""
    content: List[Any]  # List of content blocks (text, tool_use)
    stop_reason: str
    model: str
    usage: Optional[Dict[str, int]] = None


class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All providers must implement this interface to support:
    - Vision/screenshot analysis
    - Tool calling (computer use)
    - Multi-turn conversations
    """
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for the provider.
            model: Model name to use.
        """
        self.api_key = api_key
        self.model = model
    
    @classmethod
    @abstractmethod
    def get_info(cls) -> ProviderInfo:
        """Get information about this provider."""
        pass
    
    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """Check if this provider is available (API key set)."""
        pass
    
    @classmethod
    @abstractmethod
    def get_default_model(cls) -> str:
        """Get the default model for this provider."""
        pass
    
    @abstractmethod
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List[Dict[str, Any]],
        max_tokens: int
    ) -> ProviderResponse:
        """
        Create a message with the provider's API.
        
        Args:
            messages: List of message dicts with role and content.
            system: System prompt.
            tools: List of tool definitions.
            max_tokens: Maximum tokens to generate.
            
        Returns:
            ProviderResponse with standardized format.
        """
        pass
    
    @abstractmethod
    def format_image_content(self, base64_data: str, media_type: str = "image/png") -> Dict[str, Any]:
        """
        Format image content for this provider.
        
        Args:
            base64_data: Base64 encoded image data.
            media_type: Media type of the image.
            
        Returns:
            Provider-specific image content block.
        """
        pass
    
    @abstractmethod
    def parse_tool_calls(self, response: ProviderResponse) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Parse tool calls from provider response.
        
        Args:
            response: Provider response.
            
        Returns:
            List of tuples: (tool_use_id, tool_name, tool_input)
        """
        pass
    
    @abstractmethod
    def format_tool_result(
        self,
        tool_use_id: str,
        result: str,
        is_error: bool = False
    ) -> Dict[str, Any]:
        """
        Format a tool result for this provider.
        
        Args:
            tool_use_id: ID of the tool use.
            result: Result text.
            is_error: Whether this is an error result.
            
        Returns:
            Provider-specific tool result format.
        """
        pass


class ProviderError(Exception):
    """Base exception for provider errors."""
    pass


class ProviderAPIError(ProviderError):
    """Error calling provider API."""
    pass


class ProviderNotAvailableError(ProviderError):
    """Provider not available (missing API key)."""
    pass

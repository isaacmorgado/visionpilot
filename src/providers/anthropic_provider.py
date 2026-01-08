"""
Anthropic Claude provider implementation.

Supports Claude's Computer Use API with native vision and tool calling.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import anthropic

from .base import (
    BaseLLMProvider,
    ProviderAPIError,
    ProviderInfo,
    ProviderNotAvailableError,
    ProviderResponse,
    ProviderType,
)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude provider with Computer Use API support.
    
    Best for:
    - Computer Use tasks (native API support)
    - Vision analysis
    - Tool calling
    
    Cost: $$$ (highest tier)
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key. If None, uses ANTHROPIC_API_KEY env var.
            model: Model to use. If None, uses default.
        """
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ProviderNotAvailableError(
                "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
            )
        
        model = model or self.get_default_model()
        super().__init__(api_key, model)
        
        self.client = anthropic.Anthropic(api_key=api_key)
    
    @classmethod
    def get_info(cls) -> ProviderInfo:
        """Get information about Anthropic provider."""
        return ProviderInfo(
            name="Anthropic Claude",
            type=ProviderType.ANTHROPIC,
            supports_vision=True,
            supports_computer_use=True,
            cost_per_1m_tokens=15.0,  # Approximate for Claude Sonnet
            free_tier=False,
            description="Best for computer use tasks with native API support"
        )
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Anthropic API key is available."""
        return bool(os.environ.get("ANTHROPIC_API_KEY"))
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default Anthropic model."""
        return os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List[Dict[str, Any]],
        max_tokens: int
    ) -> ProviderResponse:
        """
        Create a message with Anthropic API.
        
        Args:
            messages: List of message dicts.
            system: System prompt.
            tools: List of tool definitions.
            max_tokens: Maximum tokens.
            
        Returns:
            Standardized ProviderResponse.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system,
                tools=tools,
                messages=messages
            )
            
            return ProviderResponse(
                content=response.content,
                stop_reason=response.stop_reason,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            )
        except anthropic.APIError as e:
            raise ProviderAPIError(f"Anthropic API error: {e}")
    
    def format_image_content(self, base64_data: str, media_type: str = "image/png") -> Dict[str, Any]:
        """
        Format image for Anthropic.
        
        Args:
            base64_data: Base64 encoded image.
            media_type: Image media type.
            
        Returns:
            Anthropic image content block.
        """
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": base64_data
            }
        }
    
    def parse_tool_calls(self, response: ProviderResponse) -> List[Tuple[str, str, Dict[str, Any]]]:
        """
        Parse tool calls from Anthropic response.
        
        Args:
            response: Provider response.
            
        Returns:
            List of (tool_use_id, tool_name, tool_input) tuples.
        """
        tool_calls = []
        
        for block in response.content:
            if hasattr(block, "type") and block.type == "tool_use":
                tool_calls.append((
                    block.id,
                    block.name,
                    block.input
                ))
        
        return tool_calls
    
    def format_tool_result(
        self,
        tool_use_id: str,
        result: str,
        is_error: bool = False
    ) -> Dict[str, Any]:
        """
        Format tool result for Anthropic.
        
        Args:
            tool_use_id: ID of the tool use.
            result: Result text.
            is_error: Whether this is an error.
            
        Returns:
            Anthropic tool result block.
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
            "is_error": is_error
        }

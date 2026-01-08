"""
Featherless.ai provider implementation.

Supports hosted open-source models via OpenAI-compatible API.
Check for vision-capable models.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import requests

from .base import (
    BaseLLMProvider,
    ProviderAPIError,
    ProviderInfo,
    ProviderNotAvailableError,
    ProviderResponse,
    ProviderType,
)


class FeatherlessProvider(BaseLLMProvider):
    """
    Featherless.ai provider with OpenAI-compatible API.
    
    Best for:
    - Access to open-source models
    - Cost-effective operation
    - Experimental model access
    
    Cost: $ (varies by model) - generally cheaper than proprietary APIs
    
    Note: Vision support depends on the specific model selected.
    """
    
    BASE_URL = "https://api.featherless.ai/v1"
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Featherless provider.
        
        Args:
            api_key: Featherless API key. If None, uses FEATHERLESS_API_KEY env var.
            model: Model to use. If None, uses default.
        """
        api_key = api_key or os.environ.get("FEATHERLESS_API_KEY")
        if not api_key:
            raise ProviderNotAvailableError(
                "Featherless API key not found. Set FEATHERLESS_API_KEY environment variable."
            )
        
        model = model or self.get_default_model()
        super().__init__(api_key, model)
    
    @classmethod
    def get_info(cls) -> ProviderInfo:
        """Get information about Featherless provider."""
        return ProviderInfo(
            name="Featherless.ai",
            type=ProviderType.FEATHERLESS,
            supports_vision=False,  # Depends on model - most don't support vision yet
            supports_computer_use=True,  # Via function calling
            cost_per_1m_tokens=2.0,  # Approximate, varies by model
            free_tier=False,
            description="Access to open-source models with competitive pricing"
        )
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Featherless API key is available."""
        return bool(os.environ.get("FEATHERLESS_API_KEY"))
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default Featherless model."""
        return os.environ.get("FEATHERLESS_MODEL", "meta-llama/llama-3.1-70b-instruct")
    
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List[Dict[str, Any]],
        max_tokens: int
    ) -> ProviderResponse:
        """
        Create a message with Featherless API (OpenAI-compatible).
        
        Args:
            messages: List of message dicts.
            system: System prompt.
            tools: List of tool definitions.
            max_tokens: Maximum tokens.
            
        Returns:
            Standardized ProviderResponse.
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = self._convert_messages(messages, system)
            
            # Convert tools to OpenAI function format
            openai_tools = self._convert_tools(tools) if tools else None
            
            # Create request payload
            payload = {
                "model": self.model,
                "messages": openai_messages,
                "max_tokens": max_tokens,
            }
            
            if openai_tools:
                payload["tools"] = openai_tools
                payload["tool_choice"] = "auto"
            
            # Make request to Featherless API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code != 200:
                raise ProviderAPIError(
                    f"Featherless API error: {response.status_code} - {response.text}"
                )
            
            data = response.json()
            
            # Convert to standard format
            return self._convert_response(data)
            
        except requests.RequestException as e:
            raise ProviderAPIError(f"Featherless API request error: {e}")
        except Exception as e:
            raise ProviderAPIError(f"Featherless API error: {e}")
    
    def _convert_messages(
        self,
        messages: List[Dict[str, Any]],
        system: str
    ) -> List[Dict[str, Any]]:
        """Convert Anthropic-style messages to OpenAI format."""
        openai_messages = []
        
        # Add system message first
        if system:
            openai_messages.append({
                "role": "system",
                "content": system
            })
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            # Handle different content types
            if isinstance(content, str):
                openai_messages.append({
                    "role": role,
                    "content": content
                })
            elif isinstance(content, list):
                # For Featherless, flatten to text (most models don't support vision)
                text_parts = []
                
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item["text"])
                        elif item.get("type") == "image":
                            # Skip images for now - most Featherless models don't support vision
                            text_parts.append("[Image content - not supported by this model]")
                        elif item.get("type") == "tool_result":
                            # Tool results become separate messages
                            openai_messages.append({
                                "role": "tool",
                                "tool_call_id": item["tool_use_id"],
                                "content": item.get("content", "")
                            })
                    else:
                        text_parts.append(str(item))
                
                if text_parts:
                    openai_messages.append({
                        "role": role,
                        "content": " ".join(text_parts)
                    })
        
        return openai_messages
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic tool format to OpenAI function format."""
        openai_tools = []
        
        for tool in tools:
            if tool.get("name") == "computer":
                # Convert computer tool to OpenAI function
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": "computer",
                        "description": "Control computer via mouse, keyboard, and screenshots",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "action": {
                                    "type": "string",
                                    "description": "Action to perform",
                                    "enum": [
                                        "screenshot", "mouse_move", "left_click",
                                        "right_click", "double_click", "key", "type", "scroll"
                                    ]
                                },
                                "coordinate": {
                                    "type": "array",
                                    "description": "X,Y coordinates for mouse actions",
                                    "items": {"type": "integer"}
                                },
                                "text": {
                                    "type": "string",
                                    "description": "Text to type or key to press"
                                }
                            },
                            "required": ["action"]
                        }
                    }
                })
        
        return openai_tools
    
    def _convert_response(self, data: Dict[str, Any]) -> ProviderResponse:
        """Convert Featherless response to standard format."""
        content = []
        choice = data["choices"][0]
        message = choice["message"]
        
        # Add text content
        if message.get("content"):
            content.append(type('TextBlock', (), {
                'type': 'text',
                'text': message["content"]
            })())
        
        # Add tool calls
        if message.get("tool_calls"):
            import json
            for tool_call in message["tool_calls"]:
                tool_input = json.loads(tool_call["function"]["arguments"])
                
                content.append(type('ToolUseBlock', (), {
                    'type': 'tool_use',
                    'id': tool_call["id"],
                    'name': tool_call["function"]["name"],
                    'input': tool_input
                })())
        
        # Map finish reason
        finish_reason_map = {
            "stop": "end_turn",
            "length": "max_tokens",
            "tool_calls": "tool_use",
            "content_filter": "end_turn",
        }
        stop_reason = finish_reason_map.get(choice["finish_reason"], "end_turn")
        
        # Extract usage
        usage = None
        if data.get("usage"):
            usage = {
                "input_tokens": data["usage"]["prompt_tokens"],
                "output_tokens": data["usage"]["completion_tokens"]
            }
        
        return ProviderResponse(
            content=content,
            stop_reason=stop_reason,
            model=data.get("model", self.model),
            usage=usage
        )
    
    def format_image_content(self, base64_data: str, media_type: str = "image/png") -> Dict[str, Any]:
        """
        Format image for Featherless.
        
        Note: Most Featherless models don't support vision yet.
        
        Args:
            base64_data: Base64 encoded image.
            media_type: Image media type.
            
        Returns:
            Image content block (may not be supported).
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
        Parse tool calls from Featherless response.
        
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
        Format tool result for Featherless.
        
        Args:
            tool_use_id: ID of the tool use.
            result: Result text.
            is_error: Whether this is an error.
            
        Returns:
            Tool result block.
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
            "is_error": is_error
        }

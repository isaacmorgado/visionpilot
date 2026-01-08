"""
OpenAI GPT provider implementation.

Supports GPT-4o and GPT-4o-mini with vision and function calling.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import openai

from .base import (
    BaseLLMProvider,
    ProviderAPIError,
    ProviderInfo,
    ProviderNotAvailableError,
    ProviderResponse,
    ProviderType,
)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI GPT provider with vision and function calling support.
    
    Best for:
    - ChatGPT subscription users (included in subscription)
    - Vision analysis
    - Reliable function calling
    
    Cost: $$ (mid-tier) - cheaper if using ChatGPT subscription
    """
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key. If None, uses OPENAI_API_KEY env var.
            model: Model to use. If None, uses default.
        """
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ProviderNotAvailableError(
                "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
            )
        
        model = model or self.get_default_model()
        super().__init__(api_key, model)
        
        self.client = openai.OpenAI(api_key=api_key)
    
    @classmethod
    def get_info(cls) -> ProviderInfo:
        """Get information about OpenAI provider."""
        return ProviderInfo(
            name="OpenAI GPT",
            type=ProviderType.OPENAI,
            supports_vision=True,
            supports_computer_use=True,  # Via function calling
            cost_per_1m_tokens=5.0,  # Approximate for GPT-4o
            free_tier=False,
            description="Good for ChatGPT subscription users with vision support"
        )
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if OpenAI API key is available."""
        return bool(os.environ.get("OPENAI_API_KEY"))
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default OpenAI model."""
        return os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List[Dict[str, Any]],
        max_tokens: int
    ) -> ProviderResponse:
        """
        Create a message with OpenAI API.
        
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
            
            # Create completion
            kwargs = {
                "model": self.model,
                "messages": openai_messages,
                "max_tokens": max_tokens,
            }
            
            if openai_tools:
                kwargs["tools"] = openai_tools
                kwargs["tool_choice"] = "auto"
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Convert to standard format
            return self._convert_response(response)
            
        except openai.APIError as e:
            raise ProviderAPIError(f"OpenAI API error: {e}")
    
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
                # Build content array for multimodal
                openai_content = []
                
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            openai_content.append({
                                "type": "text",
                                "text": item["text"]
                            })
                        elif item.get("type") == "image":
                            # Convert base64 image to OpenAI format
                            openai_content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{item['source']['media_type']};base64,{item['source']['data']}"
                                }
                            })
                        elif item.get("type") == "tool_result":
                            # Tool results become tool messages
                            openai_messages.append({
                                "role": "tool",
                                "tool_call_id": item["tool_use_id"],
                                "content": item.get("content", "")
                            })
                    else:
                        openai_content.append({
                            "type": "text",
                            "text": str(item)
                        })
                
                if openai_content:
                    openai_messages.append({
                        "role": role,
                        "content": openai_content
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
    
    def _convert_response(self, response: Any) -> ProviderResponse:
        """Convert OpenAI response to standard format."""
        content = []
        choice = response.choices[0]
        message = choice.message
        
        # Add text content
        if message.content:
            content.append(type('TextBlock', (), {
                'type': 'text',
                'text': message.content
            })())
        
        # Add tool calls
        if message.tool_calls:
            for tool_call in message.tool_calls:
                import json
                tool_input = json.loads(tool_call.function.arguments)
                
                content.append(type('ToolUseBlock', (), {
                    'type': 'tool_use',
                    'id': tool_call.id,
                    'name': tool_call.function.name,
                    'input': tool_input
                })())
        
        # Map finish reason
        finish_reason_map = {
            "stop": "end_turn",
            "length": "max_tokens",
            "tool_calls": "tool_use",
            "content_filter": "end_turn",
        }
        stop_reason = finish_reason_map.get(choice.finish_reason, "end_turn")
        
        # Extract usage
        usage = None
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens
            }
        
        return ProviderResponse(
            content=content,
            stop_reason=stop_reason,
            model=response.model,
            usage=usage
        )
    
    def format_image_content(self, base64_data: str, media_type: str = "image/png") -> Dict[str, Any]:
        """
        Format image for OpenAI.
        
        Args:
            base64_data: Base64 encoded image.
            media_type: Image media type.
            
        Returns:
            OpenAI image content block.
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
        Parse tool calls from OpenAI response.
        
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
        Format tool result for OpenAI.
        
        Args:
            tool_use_id: ID of the tool use.
            result: Result text.
            is_error: Whether this is an error.
            
        Returns:
            OpenAI tool result block.
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
            "is_error": is_error
        }

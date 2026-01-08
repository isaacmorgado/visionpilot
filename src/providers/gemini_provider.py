"""
Google Gemini provider implementation.

Supports Gemini with vision capabilities and tool calling.
Free tier available for cost-effective operation.
"""

import os
from typing import Any, Dict, List, Optional, Tuple

import google.generativeai as genai

from .base import (
    BaseLLMProvider,
    ProviderAPIError,
    ProviderInfo,
    ProviderNotAvailableError,
    ProviderResponse,
    ProviderType,
)


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini provider with vision and tool calling support.
    
    Best for:
    - Cost-effective operation (FREE tier available)
    - Vision analysis
    - Fast responses
    
    Cost: FREE (gemini-2.0-flash-exp) or $ (paid tier)
    """
    
    # Gemini tool format mapping
    TOOL_TYPE_MAPPING = {
        "computer": "computer_control"
    }
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key. If None, uses GOOGLE_API_KEY env var.
            model: Model to use. If None, uses default (free tier).
        """
        api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ProviderNotAvailableError(
                "Google API key not found. Set GOOGLE_API_KEY environment variable."
            )
        
        model = model or self.get_default_model()
        super().__init__(api_key, model)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Create model instance
        self.genai_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=None  # Will be set per request
        )
    
    @classmethod
    def get_info(cls) -> ProviderInfo:
        """Get information about Gemini provider."""
        return ProviderInfo(
            name="Google Gemini",
            type=ProviderType.GEMINI,
            supports_vision=True,
            supports_computer_use=True,  # Via function calling
            cost_per_1m_tokens=0.0,  # FREE tier available
            free_tier=True,
            description="Best for cost-effective operation with generous free tier"
        )
    
    @classmethod
    def is_available(cls) -> bool:
        """Check if Google API key is available."""
        return bool(os.environ.get("GOOGLE_API_KEY"))
    
    @classmethod
    def get_default_model(cls) -> str:
        """Get default Gemini model (free tier)."""
        return os.environ.get("GEMINI_MODEL", "gemini-2.0-flash-exp")
    
    def create_message(
        self,
        messages: List[Dict[str, Any]],
        system: str,
        tools: List[Dict[str, Any]],
        max_tokens: int
    ) -> ProviderResponse:
        """
        Create a message with Gemini API.
        
        Args:
            messages: List of message dicts.
            system: System prompt.
            tools: List of tool definitions.
            max_tokens: Maximum tokens.
            
        Returns:
            Standardized ProviderResponse.
        """
        try:
            # Convert messages to Gemini format
            gemini_messages = self._convert_messages(messages)
            
            # Convert tools to Gemini function declarations
            gemini_tools = self._convert_tools(tools) if tools else None
            
            # Create model with system instruction
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system if system else None
            )
            
            # Generate content
            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=1.0,
            )
            
            # Start chat or generate
            if len(gemini_messages) > 1:
                # Multi-turn conversation
                chat = model.start_chat(history=gemini_messages[:-1])
                response = chat.send_message(
                    gemini_messages[-1]["parts"],
                    generation_config=generation_config,
                    tools=gemini_tools
                )
            else:
                # Single turn
                response = model.generate_content(
                    gemini_messages[0]["parts"],
                    generation_config=generation_config,
                    tools=gemini_tools
                )
            
            # Convert response to standard format
            return self._convert_response(response)
            
        except Exception as e:
            raise ProviderAPIError(f"Gemini API error: {e}")
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Anthropic-style messages to Gemini format."""
        gemini_messages = []
        
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            content = msg["content"]
            
            # Handle different content types
            if isinstance(content, str):
                parts = [content]
            elif isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            parts.append(item["text"])
                        elif item.get("type") == "image":
                            # Convert base64 image to Gemini format
                            import base64
                            from PIL import Image
                            import io
                            
                            image_data = base64.b64decode(item["source"]["data"])
                            image = Image.open(io.BytesIO(image_data))
                            parts.append(image)
                        elif item.get("type") == "tool_result":
                            # Add tool result as text
                            parts.append(f"Tool result: {item.get('content', '')}")
                    else:
                        parts.append(str(item))
            else:
                parts = [str(content)]
            
            gemini_messages.append({
                "role": role,
                "parts": parts
            })
        
        return gemini_messages
    
    def _convert_tools(self, tools: List[Dict[str, Any]]) -> List[Any]:
        """Convert Anthropic tool format to Gemini function declarations."""
        gemini_tools = []
        
        for tool in tools:
            if tool.get("name") == "computer":
                # Convert computer tool to Gemini function
                function_declaration = genai.types.FunctionDeclaration(
                    name="computer",
                    description="Control computer via mouse, keyboard, and screenshots",
                    parameters={
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
                )
                gemini_tools.append(genai.types.Tool(
                    function_declarations=[function_declaration]
                ))
        
        return gemini_tools
    
    def _convert_response(self, response: Any) -> ProviderResponse:
        """Convert Gemini response to standard format."""
        content = []
        
        # Check if response has function calls
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            
            if hasattr(candidate.content, 'parts'):
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        # Text content
                        content.append(type('TextBlock', (), {
                            'type': 'text',
                            'text': part.text
                        })())
                    elif hasattr(part, 'function_call'):
                        # Function call (tool use)
                        fc = part.function_call
                        tool_input = dict(fc.args) if fc.args else {}
                        
                        content.append(type('ToolUseBlock', (), {
                            'type': 'tool_use',
                            'id': f"tool_{hash(str(fc))}",  # Generate ID
                            'name': fc.name,
                            'input': tool_input
                        })())
            
            # Determine stop reason
            finish_reason = candidate.finish_reason
            if finish_reason == 1:  # STOP
                stop_reason = "end_turn"
            elif finish_reason == 2:  # MAX_TOKENS
                stop_reason = "max_tokens"
            else:
                stop_reason = "end_turn"
        else:
            # Fallback
            stop_reason = "end_turn"
            if hasattr(response, 'text'):
                content.append(type('TextBlock', (), {
                    'type': 'text',
                    'text': response.text
                })())
        
        return ProviderResponse(
            content=content,
            stop_reason=stop_reason,
            model=self.model,
            usage=None  # Gemini doesn't always provide usage
        )
    
    def format_image_content(self, base64_data: str, media_type: str = "image/png") -> Dict[str, Any]:
        """
        Format image for Gemini.
        
        Args:
            base64_data: Base64 encoded image.
            media_type: Image media type.
            
        Returns:
            Gemini image content block.
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
        Parse tool calls from Gemini response.
        
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
        Format tool result for Gemini.
        
        Args:
            tool_use_id: ID of the tool use.
            result: Result text.
            is_error: Whether this is an error.
            
        Returns:
            Gemini tool result block.
        """
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": result,
            "is_error": is_error
        }

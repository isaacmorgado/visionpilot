"""
Multi-Provider Computer Use Agent implementation.

Implements the agent loop pattern for interacting with various LLM providers
that support vision and computer control capabilities.
Based on the anthropic-quickstarts reference implementation.
"""

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from PIL import Image

from .computer import AppleScriptRunner, ComputerController, get_tool_definition
from .screen import ScreenCapture
from .providers import create_provider, get_available_providers, ProviderType
from .providers.base import BaseLLMProvider, ProviderNotAvailableError


class StopReason(str, Enum):
    """Reasons for stopping the agent loop."""
    END_TURN = "end_turn"
    TOOL_USE = "tool_use"
    MAX_TOKENS = "max_tokens"
    STOP_SEQUENCE = "stop_sequence"


@dataclass
class AgentConfig:
    """Configuration for the Computer Use agent."""
    model: Optional[str] = None  # If None, uses provider default
    max_tokens: int = 4096
    max_iterations: int = 50
    max_actions_per_session: int = 100
    action_delay: float = 0.5
    screenshot_on_tool_result: bool = True
    system_prompt: Optional[str] = None
    provider: Optional[str] = None  # Provider type or "auto"
    
    def __post_init__(self):
        if self.system_prompt is None:
            self.system_prompt = self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        return """You are an AI assistant with the ability to control a computer.
You can see the screen through screenshots and interact with it using mouse and keyboard actions.

When given a task:
1. First, analyze the current screen state by taking a screenshot
2. Plan the steps needed to accomplish the task
3. Execute actions one at a time, verifying results with screenshots
4. Report when the task is complete or if you encounter issues

Available actions:
- screenshot: Capture the current screen
- mouse_move: Move mouse to coordinates [x, y]
- left_click: Click at coordinates [x, y]
- right_click: Right-click at coordinates [x, y]
- double_click: Double-click at coordinates [x, y]
- key: Press a key or key combination (e.g., "Return", "ctrl+c", "command+shift+s")
- type: Type text
- scroll: Scroll at coordinates (positive = up, negative = down)
- cursor_position: Get current cursor position

Be precise with coordinates. The screen dimensions will be provided.
Always take a screenshot after actions to verify the result.
"""


@dataclass
class AgentMessage:
    """A message in the agent conversation."""
    role: str  # "user" or "assistant"
    content: Union[str, List[Dict[str, Any]]]


@dataclass
class AgentResult:
    """Result of an agent run."""
    success: bool
    message: str
    iterations: int
    actions_taken: int
    final_screenshot: Optional[Image.Image] = None
    conversation: List[AgentMessage] = field(default_factory=list)
    error: Optional[str] = None


class ComputerUseAgent:
    """
    Agent that uses LLM providers to control a computer.
    
    Implements the standard agent loop:
    1. Send message/screenshot to LLM
    2. LLM responds with tool use requests
    3. Execute tools and capture results
    4. Send results back to LLM
    5. Repeat until task complete or max iterations
    
    Supports multiple providers: Anthropic, Gemini, OpenAI, Featherless
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        config: Optional[AgentConfig] = None,
        on_action: Optional[Callable[[str, Dict], None]] = None,
        on_screenshot: Optional[Callable[[Image.Image], None]] = None,
        provider: Optional[BaseLLMProvider] = None
    ):
        """
        Initialize the Computer Use agent.
        
        Args:
            api_key: API key for the selected provider. If None, uses environment.
            config: Agent configuration.
            on_action: Callback for when an action is executed.
            on_screenshot: Callback for when a screenshot is taken.
            provider: Pre-configured provider instance. If None, auto-selects.
        """
        self.config = config or AgentConfig()
        
        # Initialize provider
        if provider:
            self.provider = provider
        else:
            try:
                self.provider = create_provider(
                    provider_type=self.config.provider,
                    api_key=api_key,
                    model=self.config.model
                )
            except ProviderNotAvailableError as e:
                raise ValueError(str(e))
        
        # Log selected provider
        provider_info = self.provider.get_info()
        print(f"Using provider: {provider_info.name} ({provider_info.model})")
        if provider_info.supports_free_tier:
            print("  ✓ Free tier available")
        
        # Initialize screen and controller
        self.screen = ScreenCapture()
        self.controller = ComputerController(
            screen=self.screen,
            action_delay=self.config.action_delay
        )
        
        # Callbacks
        self.on_action = on_action
        self.on_screenshot = on_screenshot
        
        # Conversation state
        self.messages: List[Dict[str, Any]] = []
        self._iteration = 0
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """Get the tools list for the API call."""
        return [get_tool_definition()]
    
    def _create_screenshot_content(self) -> Dict[str, Any]:
        """Create screenshot content block for API."""
        base64_data, image = self.screen.capture_base64(save=True)
        
        if self.on_screenshot:
            self.on_screenshot(image)
        
        return {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_data
            }
        }
    
    def _process_tool_call(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> Tuple[str, Optional[Image.Image]]:
        """
        Process a tool call from Claude.
        
        Args:
            tool_name: Name of the tool to execute.
            tool_input: Input parameters for the tool.
            
        Returns:
            Tuple of (result_message, screenshot_or_none).
        """
        if tool_name != "computer":
            return f"Unknown tool: {tool_name}", None
        
        action = tool_input.get("action", "")
        coordinate = tool_input.get("coordinate")
        text = tool_input.get("text")
        
        if self.on_action:
            self.on_action(action, tool_input)
        
        result, image = self.controller.execute(action, coordinate, text)
        
        return result, image
    
    def _create_tool_result(
        self,
        tool_use_id: str,
        result: str,
        screenshot: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        """Create a tool result message."""
        content = []
        
        # Add text result
        content.append({
            "type": "text",
            "text": result
        })
        
        # Add screenshot if available and configured
        if screenshot and self.config.screenshot_on_tool_result:
            base64_data = self.screen.to_base64(screenshot)
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64_data
                }
            })
        elif self.config.screenshot_on_tool_result:
            # Take a new screenshot
            content.append(self._create_screenshot_content())
        
        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": content
        }
    
    def run(self, task: str, initial_screenshot: bool = True) -> AgentResult:
        """
        Run the agent to complete a task.
        
        Args:
            task: The task description to complete.
            initial_screenshot: Whether to include initial screenshot.
            
        Returns:
            AgentResult with success status and details.
        """
        self.messages = []
        self._iteration = 0
        self.controller.reset_action_count()
        
        # Create initial user message
        user_content = []
        
        if initial_screenshot:
            user_content.append(self._create_screenshot_content())
        
        user_content.append({
            "type": "text",
            "text": task
        })
        
        self.messages.append({
            "role": "user",
            "content": user_content
        })
        
        # Main agent loop
        while self._iteration < self.config.max_iterations:
            self._iteration += 1
            
            # Check action limit
            if self.controller.action_count >= self.config.max_actions_per_session:
                return AgentResult(
                    success=False,
                    message="Maximum actions per session reached",
                    iterations=self._iteration,
                    actions_taken=self.controller.action_count,
                    error="Action limit exceeded"
                )
            
            try:
                # Call LLM provider
                response = self.provider.create_message(
                    messages=self.messages,
                    max_tokens=self.config.max_tokens,
                    system=self.config.system_prompt,
                    tools=self._get_tools()
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    message=f"API error: {e}",
                    iterations=self._iteration,
                    actions_taken=self.controller.action_count,
                    error=str(e)
                )
            
            # Add assistant response to messages
            self.messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            # Check stop reason
            if response.stop_reason == "end_turn":
                # Extract final text message
                final_message = ""
                for block in response.content:
                    if hasattr(block, "text"):
                        final_message = block.text
                        break
                
                return AgentResult(
                    success=True,
                    message=final_message,
                    iterations=self._iteration,
                    actions_taken=self.controller.action_count,
                    final_screenshot=self.screen.capture(save=True)
                )
            
            elif response.stop_reason == "tool_use":
                # Process tool calls
                tool_results = []
                
                for block in response.content:
                    if hasattr(block, "type") and block.type == "tool_use":
                        result, screenshot = self._process_tool_call(
                            block.name,
                            block.input
                        )
                        
                        tool_results.append(
                            self._create_tool_result(
                                block.id,
                                result,
                                screenshot
                            )
                        )
                
                # Add tool results to messages
                self.messages.append({
                    "role": "user",
                    "content": tool_results
                })
            
            else:
                # Unexpected stop reason
                return AgentResult(
                    success=False,
                    message=f"Unexpected stop reason: {response.stop_reason}",
                    iterations=self._iteration,
                    actions_taken=self.controller.action_count,
                    error=f"Stop reason: {response.stop_reason}"
                )
            
            # Small delay between iterations
            time.sleep(0.1)
        
        # Max iterations reached
        return AgentResult(
            success=False,
            message="Maximum iterations reached",
            iterations=self._iteration,
            actions_taken=self.controller.action_count,
            error="Iteration limit exceeded"
        )
    
    def run_with_callback(
        self,
        task: str,
        on_iteration: Optional[Callable[[int, Dict], None]] = None
    ) -> AgentResult:
        """
        Run agent with iteration callback for progress tracking.
        
        Args:
            task: The task to complete.
            on_iteration: Callback called after each iteration.
            
        Returns:
            AgentResult.
        """
        # Store original callback and wrap
        original_action = self.on_action
        
        def wrapped_action(action: str, params: Dict):
            if original_action:
                original_action(action, params)
            if on_iteration:
                on_iteration(self._iteration, {"action": action, "params": params})
        
        self.on_action = wrapped_action
        
        try:
            return self.run(task)
        finally:
            self.on_action = original_action


def create_agent(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    max_iterations: int = 50,
    provider: Optional[str] = None
) -> ComputerUseAgent:
    """
    Factory function to create a configured agent.
    
    Args:
        api_key: API key for the selected provider. If None, uses environment.
        model: Model to use. If None, uses provider default.
        max_iterations: Maximum iterations per run.
        provider: Provider type ("anthropic", "gemini", "openai", "featherless")
                 or "auto" for automatic selection. Defaults to "auto".
        
    Returns:
        Configured ComputerUseAgent with auto-selected or specified provider.
        
    Examples:
        # Auto-select provider (prefers free tier)
        agent = create_agent()
        
        # Use specific provider
        agent = create_agent(provider="gemini")
        
        # Use specific model
        agent = create_agent(provider="openai", model="gpt-4o")
    """
    config = AgentConfig(
        model=model,
        max_iterations=max_iterations,
        provider=provider
    )
    return ComputerUseAgent(api_key=api_key, config=config)


if __name__ == "__main__":
    # Quick test (requires API key)
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.agent 'task description'")
        sys.exit(1)
    
    task = sys.argv[1]
    
    def on_action(action: str, params: Dict):
        print(f"  Action: {action} - {params}")
    
    agent = create_agent()
    agent.on_action = on_action
    
    print(f"Starting task: {task}")
    result = agent.run(task)
    
    print(f"\nResult: {'Success' if result.success else 'Failed'}")
    print(f"Message: {result.message}")
    print(f"Iterations: {result.iterations}")
    print(f"Actions: {result.actions_taken}")
    
    if result.error:
        print(f"Error: {result.error}")

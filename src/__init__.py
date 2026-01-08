"""
Autonomous Computer Control System

A system for autonomous computer control using Claude's Computer Use API.
Provides mouse/keyboard control, screen capture, and AI-powered task execution.
"""

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

__version__ = "0.1.0"

from .agent import (
    AgentConfig,
    AgentMessage,
    AgentResult,
    ComputerUseAgent,
    StopReason,
    create_agent,
)
from .computer import (
    Action,
    AppleScriptRunner,
    ComputerController,
    get_tool_definition,
)
from .logging_config import (
    ActionLogger,
    get_logger,
    setup_logging,
)
from .screen import ScreenCapture

__all__ = [
    # Version
    "__version__",
    # Agent
    "AgentConfig",
    "AgentMessage",
    "AgentResult",
    "ComputerUseAgent",
    "StopReason",
    "create_agent",
    # Computer Control
    "Action",
    "AppleScriptRunner",
    "ComputerController",
    "get_tool_definition",
    # Screen
    "ScreenCapture",
    # Logging
    "ActionLogger",
    "get_logger",
    "setup_logging",
]

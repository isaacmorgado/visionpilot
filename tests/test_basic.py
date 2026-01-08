"""
Basic tests for the Autonomous Computer Control System.

These tests verify the core functionality without requiring API keys.
"""

import pytest
from unittest.mock import MagicMock, patch


def test_imports():
    """Test that all modules can be imported."""
    from src import (
        AgentConfig,
        AgentMessage,
        AgentResult,
        ComputerUseAgent,
        StopReason,
        create_agent,
        Action,
        AppleScriptRunner,
        ComputerController,
        get_tool_definition,
        ScreenCapture,
        ActionLogger,
        get_logger,
        setup_logging,
    )
    assert True


def test_agent_config_defaults():
    """Test AgentConfig has sensible defaults."""
    from src.agent import AgentConfig
    
    config = AgentConfig()
    
    assert config.model == "claude-sonnet-4-20250514"
    assert config.max_tokens == 4096
    assert config.max_iterations == 50
    assert config.max_actions_per_session == 100
    assert config.action_delay == 0.5
    assert config.screenshot_on_tool_result is True
    assert config.system_prompt is not None


def test_action_enum():
    """Test Action enum values."""
    from src.computer import Action
    
    assert Action.SCREENSHOT == "screenshot"
    assert Action.LEFT_CLICK == "left_click"
    assert Action.KEY == "key"
    assert Action.TYPE == "type"
    assert Action.MOUSE_MOVE == "mouse_move"


def test_tool_definition_format():
    """Test get_tool_definition returns correct format."""
    from src.computer import get_tool_definition
    
    with patch('pyautogui.size', return_value=(1920, 1080)):
        tool_def = get_tool_definition()
    
    assert tool_def["type"] == "computer_20241022"
    assert tool_def["name"] == "computer"
    assert "display_width_px" in tool_def
    assert "display_height_px" in tool_def
    assert "display_number" in tool_def


def test_stop_reason_enum():
    """Test StopReason enum values."""
    from src.agent import StopReason
    
    assert StopReason.END_TURN == "end_turn"
    assert StopReason.TOOL_USE == "tool_use"
    assert StopReason.MAX_TOKENS == "max_tokens"


def test_agent_result_dataclass():
    """Test AgentResult dataclass."""
    from src.agent import AgentResult
    
    result = AgentResult(
        success=True,
        message="Task completed",
        iterations=5,
        actions_taken=10
    )
    
    assert result.success is True
    assert result.message == "Task completed"
    assert result.iterations == 5
    assert result.actions_taken == 10
    assert result.final_screenshot is None
    assert result.error is None


def test_key_mapping():
    """Test key mapping contains essential keys."""
    from src.computer import KEY_MAP
    
    assert "Return" in KEY_MAP
    assert "Tab" in KEY_MAP
    assert "Escape" in KEY_MAP
    assert "Super_L" in KEY_MAP  # macOS command key
    assert KEY_MAP["Super_L"] == "command"


@patch('pyautogui.screenshot')
@patch('pyautogui.size', return_value=(1920, 1080))
def test_screen_capture_mock(mock_size, mock_screenshot):
    """Test ScreenCapture with mocked PyAutoGUI."""
    from PIL import Image
    from src.screen import ScreenCapture
    
    # Create a mock image
    mock_image = Image.new('RGB', (1920, 1080), color='red')
    mock_screenshot.return_value = mock_image
    
    screen = ScreenCapture()
    
    assert screen.width == 1920
    assert screen.height == 1080


@patch('subprocess.run')
def test_applescript_runner_mock(mock_run):
    """Test AppleScriptRunner with mocked subprocess."""
    from src.computer import AppleScriptRunner
    
    # Mock successful result
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="Safari\n",
        stderr=""
    )
    
    success, result = AppleScriptRunner.get_frontmost_app()
    
    assert success is True
    assert result == "Safari"
    mock_run.assert_called_once()


def test_logging_setup():
    """Test logging configuration."""
    from src.logging_config import setup_logging, get_logger
    
    # Should not raise
    setup_logging(level="DEBUG")
    
    logger = get_logger("test")
    assert logger is not None


def test_action_logger():
    """Test ActionLogger class."""
    from src.logging_config import ActionLogger
    
    logger = ActionLogger(session_id="test_session")
    
    assert logger.session_id == "test_session"
    assert logger._action_count == 0
    
    # Log an action
    logger.log_action(
        action="left_click",
        params={"coordinate": [100, 200]},
        result="Clicked",
        success=True
    )
    
    assert logger._action_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

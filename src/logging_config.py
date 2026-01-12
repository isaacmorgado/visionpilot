"""
Logging configuration for the Autonomous Computer Control system.

Provides structured logging with rich console output and file logging support.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Optional structlog dependency - fall back to standard logging if not available
try:
    import structlog

    HAS_STRUCTLOG = True
except ImportError:
    HAS_STRUCTLOG = False


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None, json_logs: bool = False
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file: Optional path to log file.
        json_logs: If True, output JSON formatted logs.
    """
    # Create logs directory if logging to file
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure standard logging
    log_level = getattr(logging, level.upper(), logging.INFO)

    if HAS_STRUCTLOG:
        # Use structlog if available
        shared_processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.UnicodeDecoder(),
        ]

        if json_logs:
            processors = shared_processors + [
                structlog.processors.format_exc_info,
                structlog.processors.JSONRenderer(),
            ]
        else:
            processors = shared_processors + [
                structlog.dev.ConsoleRenderer(
                    colors=True, exception_formatter=structlog.dev.plain_traceback
                )
            ]

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Configure root logger (works with or without structlog)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)

    if json_logs:
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str):
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        Configured logger (structlog if available, else standard logging).
    """
    if HAS_STRUCTLOG:
        return structlog.get_logger(name)
    else:
        return logging.getLogger(name)


class ActionLogger:
    """
    Logger specialized for tracking agent actions.

    Provides methods to log actions, screenshots, and agent decisions
    in a structured format for analysis.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the action logger.

        Args:
            session_id: Optional session identifier.
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logger = get_logger("agent.actions")
        self._action_count = 0

    def log_session_start(self, task: str, config: Dict[str, Any]) -> None:
        """Log the start of an agent session."""
        if HAS_STRUCTLOG:
            self.logger.info(
                "Session started", session_id=self.session_id, task=task, config=config
            )
        else:
            self.logger.info(f"Session started: {self.session_id}, task: {task}")

    def log_session_end(
        self, success: bool, message: str, iterations: int, actions: int
    ) -> None:
        """Log the end of an agent session."""
        if HAS_STRUCTLOG:
            self.logger.info(
                "Session ended",
                session_id=self.session_id,
                success=success,
                message=message,
                iterations=iterations,
                actions=actions,
            )
        else:
            self.logger.info(
                f"Session ended: {self.session_id}, success: {success}, message: {message}"
            )

    def log_action(
        self, action: str, params: Dict[str, Any], result: str, success: bool = True
    ) -> None:
        """Log an individual action."""
        self._action_count += 1
        if HAS_STRUCTLOG:
            self.logger.info(
                "Action executed",
                session_id=self.session_id,
                action_number=self._action_count,
                action=action,
                params=params,
                result=result,
                success=success,
            )
        else:
            self.logger.info(
                f"Action #{self._action_count}: {action}, result: {result}"
            )

    def log_screenshot(
        self, path: str, purpose: str = "capture", size: Optional[tuple] = None
    ) -> None:
        """Log a screenshot capture."""
        if HAS_STRUCTLOG:
            self.logger.debug(
                "Screenshot captured",
                session_id=self.session_id,
                path=path,
                purpose=purpose,
                size=size,
            )
        else:
            self.logger.debug(f"Screenshot captured: {path}")

    def log_api_call(
        self, model: str, tokens_in: int, tokens_out: int, stop_reason: str
    ) -> None:
        """Log an API call to Claude."""
        if HAS_STRUCTLOG:
            self.logger.debug(
                "API call completed",
                session_id=self.session_id,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                stop_reason=stop_reason,
            )
        else:
            self.logger.debug(f"API call: {model}, tokens: {tokens_in}/{tokens_out}")

    def log_decision(self, decision: str, reasoning: str) -> None:
        """Log an agent decision."""
        reasoning_short = reasoning[:200] if len(reasoning) > 200 else reasoning
        if HAS_STRUCTLOG:
            self.logger.info(
                "Agent decision",
                session_id=self.session_id,
                decision=decision,
                reasoning=reasoning_short,
            )
        else:
            self.logger.info(f"Decision: {decision}, reasoning: {reasoning_short}")

    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an error."""
        if HAS_STRUCTLOG:
            self.logger.error(
                "Error occurred",
                session_id=self.session_id,
                error=error,
                context=context or {},
            )
        else:
            self.logger.error(f"Error: {error}")


# Default logging setup
def configure_default_logging():
    """Configure logging with sensible defaults."""
    setup_logging(level="INFO", log_file=None, json_logs=False)


if __name__ == "__main__":
    # Test logging configuration
    setup_logging(level="DEBUG")

    logger = get_logger(__name__)
    logger.info("Test info message")
    logger.debug("Test debug message", extra_field="value")
    logger.warning("Test warning")

    action_logger = ActionLogger()
    action_logger.log_session_start("Test task", {"model": "claude-sonnet-4-20250514"})
    action_logger.log_action(
        "left_click", {"coordinate": [100, 200]}, "Clicked at (100, 200)"
    )
    action_logger.log_session_end(True, "Task completed", 3, 5)

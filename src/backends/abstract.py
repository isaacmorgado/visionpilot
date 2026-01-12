"""
Abstract base class for computer control backends.

Defines the interface that all backends must implement to provide
mouse, keyboard, and screen capture functionality.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from PIL import Image


class BackendType(str, Enum):
    """Supported backend types."""

    PYAUTOGUI = "pyautogui"
    MACOS = "macos"
    AUTO = "auto"


@dataclass
class BackendCapabilities:
    """
    Capabilities of a backend implementation.

    Attributes:
        name: Backend name (e.g., "PyAutoGUI", "macOS Native")
        background_capture: Can capture windows without activating them
        background_input: Can send input to background applications
        requires_accessibility: Requires macOS Accessibility permissions
        requires_screen_recording: Requires macOS Screen Recording permissions
        platform: Supported platform(s) (e.g., "any", "macOS")
        performance_multiplier: Approximate performance vs PyAutoGUI (1.0 = baseline)
    """

    name: str
    background_capture: bool
    background_input: bool
    requires_accessibility: bool
    requires_screen_recording: bool
    platform: str
    performance_multiplier: float


class AbstractBackend(ABC):
    """
    Abstract base class for computer control backends.

    All backends must implement these methods to provide unified
    interface for mouse, keyboard, and screen capture operations.
    """

    def __init__(self, action_delay: float = 0.5):
        """
        Initialize the backend.

        Args:
            action_delay: Delay between actions in seconds.
        """
        self.action_delay = action_delay
        self._action_count = 0

    @property
    def action_count(self) -> int:
        """Get the number of actions performed."""
        return self._action_count

    def reset_action_count(self) -> None:
        """Reset the action counter."""
        self._action_count = 0

    @abstractmethod
    def get_capabilities(self) -> BackendCapabilities:
        """
        Get the capabilities of this backend.

        Returns:
            BackendCapabilities describing what this backend supports.
        """
        pass

    # Screen Capture

    @abstractmethod
    def screenshot(self, save: bool = True) -> Tuple[str, Image.Image]:
        """
        Capture a screenshot.

        Args:
            save: If True, save the screenshot to disk.

        Returns:
            Tuple of (result_message, PIL Image).
        """
        pass

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions.

        Returns:
            Tuple of (width, height) in pixels.
        """
        pass

    # Mouse Operations

    @abstractmethod
    def cursor_position(self) -> Tuple[str, Tuple[int, int]]:
        """
        Get current cursor position.

        Returns:
            Tuple of (result_message, (x, y) coordinates).
        """
        pass

    @abstractmethod
    def mouse_move(self, x: int, y: int) -> str:
        """
        Move mouse cursor to coordinates.

        Args:
            x: X coordinate in pixels.
            y: Y coordinate in pixels.

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def left_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """
        Perform left mouse click.

        Args:
            x: Optional X coordinate (clicks at current position if None).
            y: Optional Y coordinate (clicks at current position if None).

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """
        Perform right mouse click.

        Args:
            x: Optional X coordinate (clicks at current position if None).
            y: Optional Y coordinate (clicks at current position if None).

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def middle_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """
        Perform middle mouse click.

        Args:
            x: Optional X coordinate (clicks at current position if None).
            y: Optional Y coordinate (clicks at current position if None).

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """
        Perform double left click.

        Args:
            x: Optional X coordinate (clicks at current position if None).
            y: Optional Y coordinate (clicks at current position if None).

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def left_click_drag(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> str:
        """
        Click and drag from start to end position.

        Args:
            start_x: Starting X coordinate.
            start_y: Starting Y coordinate.
            end_x: Ending X coordinate.
            end_y: Ending Y coordinate.

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def scroll(
        self, amount: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> str:
        """
        Scroll mouse wheel.

        Args:
            amount: Number of scroll clicks (positive=up, negative=down).
            x: Optional X coordinate to scroll at.
            y: Optional Y coordinate to scroll at.

        Returns:
            Result message.
        """
        pass

    # Keyboard Operations

    @abstractmethod
    def key_press(self, key_combo: str) -> str:
        """
        Press a key or key combination.

        Args:
            key_combo: Key or combination (e.g., "a", "ctrl+c", "command+shift+s").

        Returns:
            Result message.
        """
        pass

    @abstractmethod
    def type_text(self, text: str) -> str:
        """
        Type text string.

        Args:
            text: Text to type.

        Returns:
            Result message.
        """
        pass

    # Background Operations (Optional - not all backends support)

    def capture_window_by_pid(self, pid: int) -> Optional[Image.Image]:
        """
        Capture a specific window by process ID without activating it.

        Only supported by backends with background_capture capability.

        Args:
            pid: Process ID of the application.

        Returns:
            PIL Image of the window, or None if not supported.
        """
        return None

    def send_key_to_pid(self, pid: int, key_combo: str) -> bool:
        """
        Send keyboard input to a specific process without activating it.

        Only supported by backends with background_input capability.

        Args:
            pid: Process ID of the application.
            key_combo: Key or combination to send.

        Returns:
            True if successful, False otherwise.
        """
        return False

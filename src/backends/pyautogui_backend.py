"""
PyAutoGUI backend implementation.

Uses PyAutoGUI for cross-platform computer control. This is the baseline
implementation that requires applications to be in the foreground.

Performance: 1.0x (baseline)
Background operation: No
Platform: Any (Windows, macOS, Linux)
"""

import time
from typing import Optional, Tuple
from PIL import Image
import pyautogui

from .abstract import AbstractBackend, BackendCapabilities


# Key mapping from Computer Use API to PyAutoGUI
KEY_MAP = {
    "Return": "return",
    "enter": "return",
    "Tab": "tab",
    "Escape": "escape",
    "BackSpace": "backspace",
    "Delete": "delete",
    "space": "space",
    "Up": "up",
    "Down": "down",
    "Left": "left",
    "Right": "right",
    "Home": "home",
    "End": "end",
    "Page_Up": "pageup",
    "Page_Down": "pagedown",
    # Modifier keys
    "Control_L": "ctrl",
    "Control_R": "ctrl",
    "Alt_L": "alt",
    "Alt_R": "alt",
    "Shift_L": "shift",
    "Shift_R": "shift",
    "Super_L": "command",  # macOS command key
    "Super_R": "command",
    "Meta_L": "command",
    "Meta_R": "command",
    # Function keys
    "F1": "f1",
    "F2": "f2",
    "F3": "f3",
    "F4": "f4",
    "F5": "f5",
    "F6": "f6",
    "F7": "f7",
    "F8": "f8",
    "F9": "f9",
    "F10": "f10",
    "F11": "f11",
    "F12": "f12",
}


class PyAutoGUIBackend(AbstractBackend):
    """
    PyAutoGUI-based backend for computer control.

    This backend uses PyAutoGUI for cross-platform compatibility.
    Requires applications to be in the foreground for interaction.

    Pros:
        - Cross-platform (Windows, macOS, Linux)
        - Simple to use
        - Well-tested

    Cons:
        - Requires foreground focus
        - Slow (2-5 second window switching delays)
        - Cannot operate in background
        - User cannot work on other tasks during automation
    """

    def __init__(self, action_delay: float = 0.5, screenshot_dir: Optional[str] = None):
        """
        Initialize PyAutoGUI backend.

        Args:
            action_delay: Delay between actions in seconds.
            screenshot_dir: Directory to save screenshots (default: ./screenshots).
        """
        super().__init__(action_delay)

        # Configure PyAutoGUI
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = True

        # Screenshot configuration
        from pathlib import Path

        self.screenshot_dir = Path(screenshot_dir or "./screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    def get_capabilities(self) -> BackendCapabilities:
        """Get PyAutoGUI backend capabilities."""
        return BackendCapabilities(
            name="PyAutoGUI",
            background_capture=False,
            background_input=False,
            requires_accessibility=True,
            requires_screen_recording=True,
            platform="any",
            performance_multiplier=1.0,  # Baseline performance
        )

    # Screen Capture

    def screenshot(self, save: bool = True) -> Tuple[str, Image.Image]:
        """Capture screenshot using PyAutoGUI."""
        self._action_count += 1

        screenshot = pyautogui.screenshot()

        if save:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            screenshot.save(filepath, optimize=True)

        return "Screenshot captured", screenshot

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return pyautogui.size()

    # Mouse Operations

    def cursor_position(self) -> Tuple[str, Tuple[int, int]]:
        """Get current cursor position."""
        x, y = pyautogui.position()
        return f"Cursor position: ({x}, {y})", (x, y)

    def mouse_move(self, x: int, y: int) -> str:
        """Move mouse to coordinates."""
        self._action_count += 1
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(self.action_delay)
        return f"Moved mouse to ({x}, {y})"

    def left_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Perform left click."""
        self._action_count += 1

        if x is not None and y is not None:
            pyautogui.click(x, y, button="left")
        else:
            pyautogui.click(button="left")
            x, y = pyautogui.position()

        time.sleep(self.action_delay)
        return f"Left click at ({x}, {y})"

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Perform right click."""
        self._action_count += 1

        if x is not None and y is not None:
            pyautogui.click(x, y, button="right")
        else:
            pyautogui.click(button="right")
            x, y = pyautogui.position()

        time.sleep(self.action_delay)
        return f"Right click at ({x}, {y})"

    def middle_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Perform middle click."""
        self._action_count += 1

        if x is not None and y is not None:
            pyautogui.click(x, y, button="middle")
        else:
            pyautogui.click(button="middle")
            x, y = pyautogui.position()

        time.sleep(self.action_delay)
        return f"Middle click at ({x}, {y})"

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> str:
        """Perform double click."""
        self._action_count += 1

        if x is not None and y is not None:
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
            x, y = pyautogui.position()

        time.sleep(self.action_delay)
        return f"Double click at ({x}, {y})"

    def left_click_drag(
        self, start_x: int, start_y: int, end_x: int, end_y: int
    ) -> str:
        """Click and drag from start to end."""
        self._action_count += 1

        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=0.5)
        time.sleep(self.action_delay)

        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"

    def scroll(
        self, amount: int, x: Optional[int] = None, y: Optional[int] = None
    ) -> str:
        """Scroll mouse wheel."""
        self._action_count += 1

        if x is not None and y is not None:
            pyautogui.moveTo(x, y)

        pyautogui.scroll(amount)
        time.sleep(self.action_delay)

        return f"Scrolled {amount} clicks"

    # Keyboard Operations

    def key_press(self, key_combo: str) -> str:
        """Press a key or key combination."""
        self._action_count += 1

        # Handle key combinations (e.g., "ctrl+c", "command+shift+s")
        keys = key_combo.split("+")
        mapped_keys = []

        for key in keys:
            key = key.strip()
            mapped = KEY_MAP.get(key, key.lower())
            mapped_keys.append(mapped)

        if len(mapped_keys) == 1:
            pyautogui.press(mapped_keys[0])
        else:
            pyautogui.hotkey(*mapped_keys)

        time.sleep(self.action_delay)
        return f"Pressed key(s): {key_combo}"

    def type_text(self, text: str) -> str:
        """Type text string."""
        self._action_count += 1

        pyautogui.write(text, interval=0.02)
        time.sleep(self.action_delay)

        text_preview = text[:50] + "..." if len(text) > 50 else text
        return f"Typed text: {text_preview}"

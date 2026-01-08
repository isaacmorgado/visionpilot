"""
Computer control module for mouse and keyboard operations.

Provides a unified interface for controlling the computer using PyAutoGUI.
This module implements the tool interface expected by Claude Computer Use API.
"""

import subprocess
import time
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple

import pyautogui
from PIL import Image

from .screen import ScreenCapture

# Configure PyAutoGUI
pyautogui.PAUSE = 0.1  # Add small pause between PyAutoGUI calls
pyautogui.FAILSAFE = True  # Move mouse to corner to abort


class Action(str, Enum):
    """Actions supported by the computer tool."""
    SCREENSHOT = "screenshot"
    KEY = "key"
    TYPE = "type"
    MOUSE_MOVE = "mouse_move"
    LEFT_CLICK = "left_click"
    LEFT_CLICK_DRAG = "left_click_drag"
    RIGHT_CLICK = "right_click"
    MIDDLE_CLICK = "middle_click"
    DOUBLE_CLICK = "double_click"
    SCROLL = "scroll"
    CURSOR_POSITION = "cursor_position"


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


class ComputerController:
    """
    Controller for mouse and keyboard operations.
    
    Implements the computer tool interface expected by Claude Computer Use API.
    """
    
    def __init__(
        self,
        screen: Optional[ScreenCapture] = None,
        action_delay: float = 0.5
    ):
        """
        Initialize the computer controller.
        
        Args:
            screen: ScreenCapture instance for screenshots.
            action_delay: Delay between actions in seconds.
        """
        self.screen = screen or ScreenCapture()
        self.action_delay = action_delay
        self._action_count = 0
    
    @property
    def action_count(self) -> int:
        """Get the number of actions performed."""
        return self._action_count
    
    def reset_action_count(self) -> None:
        """Reset the action counter."""
        self._action_count = 0
    
    def execute(
        self,
        action: str,
        coordinate: Optional[List[int]] = None,
        text: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[Image.Image]]:
        """
        Execute a computer action.
        
        Args:
            action: The action to perform (see Action enum).
            coordinate: [x, y] coordinates for mouse actions.
            text: Text to type or key to press.
            
        Returns:
            Tuple of (result_message, screenshot_image or None).
        """
        self._action_count += 1
        
        action_enum = Action(action)
        
        if action_enum == Action.SCREENSHOT:
            return self._screenshot()
        
        elif action_enum == Action.CURSOR_POSITION:
            return self._get_cursor_position()
        
        elif action_enum == Action.MOUSE_MOVE:
            return self._mouse_move(coordinate)
        
        elif action_enum == Action.LEFT_CLICK:
            return self._click(coordinate, button="left")
        
        elif action_enum == Action.RIGHT_CLICK:
            return self._click(coordinate, button="right")
        
        elif action_enum == Action.MIDDLE_CLICK:
            return self._click(coordinate, button="middle")
        
        elif action_enum == Action.DOUBLE_CLICK:
            return self._double_click(coordinate)
        
        elif action_enum == Action.LEFT_CLICK_DRAG:
            return self._drag(coordinate, text)  # text contains end coordinates
        
        elif action_enum == Action.SCROLL:
            return self._scroll(coordinate, text)
        
        elif action_enum == Action.KEY:
            return self._key(text)
        
        elif action_enum == Action.TYPE:
            return self._type(text)
        
        else:
            return f"Unknown action: {action}", None
    
    def _screenshot(self) -> Tuple[str, Image.Image]:
        """Take a screenshot."""
        image = self.screen.capture(save=True)
        return "Screenshot captured", image
    
    def _get_cursor_position(self) -> Tuple[str, None]:
        """Get current cursor position."""
        x, y = pyautogui.position()
        return f"Cursor position: ({x}, {y})", None
    
    def _mouse_move(self, coordinate: Optional[List[int]]) -> Tuple[str, None]:
        """Move mouse to coordinate."""
        if not coordinate or len(coordinate) < 2:
            return "Error: coordinate required for mouse_move", None
        
        x, y = coordinate[0], coordinate[1]
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(self.action_delay)
        
        return f"Moved mouse to ({x}, {y})", None
    
    def _click(
        self,
        coordinate: Optional[List[int]],
        button: str = "left"
    ) -> Tuple[str, None]:
        """Click at coordinate."""
        if coordinate and len(coordinate) >= 2:
            x, y = coordinate[0], coordinate[1]
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)
            x, y = pyautogui.position()
        
        time.sleep(self.action_delay)
        return f"{button.capitalize()} click at ({x}, {y})", None
    
    def _double_click(self, coordinate: Optional[List[int]]) -> Tuple[str, None]:
        """Double-click at coordinate."""
        if coordinate and len(coordinate) >= 2:
            x, y = coordinate[0], coordinate[1]
            pyautogui.doubleClick(x, y)
        else:
            pyautogui.doubleClick()
            x, y = pyautogui.position()
        
        time.sleep(self.action_delay)
        return f"Double click at ({x}, {y})", None
    
    def _drag(
        self,
        start_coord: Optional[List[int]],
        end_coord_str: Optional[str]
    ) -> Tuple[str, None]:
        """Drag from start to end coordinate."""
        if not start_coord or len(start_coord) < 2:
            return "Error: start coordinate required for drag", None
        
        # Parse end coordinates from text (format: "x,y")
        if end_coord_str:
            try:
                end_parts = end_coord_str.split(",")
                end_x, end_y = int(end_parts[0]), int(end_parts[1])
            except (ValueError, IndexError):
                return "Error: invalid end coordinate format", None
        else:
            return "Error: end coordinate required for drag", None
        
        start_x, start_y = start_coord[0], start_coord[1]
        
        pyautogui.moveTo(start_x, start_y)
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=0.5)
        time.sleep(self.action_delay)
        
        return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})", None
    
    def _scroll(
        self,
        coordinate: Optional[List[int]],
        amount_str: Optional[str]
    ) -> Tuple[str, None]:
        """Scroll at coordinate."""
        # Default scroll amount
        amount = 3
        if amount_str:
            try:
                amount = int(amount_str)
            except ValueError:
                pass
        
        if coordinate and len(coordinate) >= 2:
            x, y = coordinate[0], coordinate[1]
            pyautogui.moveTo(x, y)
        
        pyautogui.scroll(amount)
        time.sleep(self.action_delay)
        
        return f"Scrolled {amount} clicks", None
    
    def _key(self, key_combo: Optional[str]) -> Tuple[str, None]:
        """Press a key or key combination."""
        if not key_combo:
            return "Error: key required", None
        
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
        return f"Pressed key(s): {key_combo}", None
    
    def _type(self, text: Optional[str]) -> Tuple[str, None]:
        """Type text."""
        if not text:
            return "Error: text required", None
        
        # Use write for ASCII, typewrite for special handling
        pyautogui.write(text, interval=0.02)
        time.sleep(self.action_delay)
        
        return f"Typed text: {text[:50]}{'...' if len(text) > 50 else ''}", None


class AppleScriptRunner:
    """
    Run AppleScript commands for macOS-specific automation.
    
    Useful for launching applications, interacting with system features,
    and controlling apps that have AppleScript support.
    """
    
    @staticmethod
    def run(script: str) -> Tuple[bool, str]:
        """
        Execute an AppleScript.
        
        Args:
            script: AppleScript code to execute.
            
        Returns:
            Tuple of (success, output_or_error).
        """
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip()
        
        except subprocess.TimeoutExpired:
            return False, "Script timed out"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def launch_app(app_name: str, wait: bool = True) -> Tuple[bool, str]:
        """
        Launch an application by name.
        
        Args:
            app_name: Name of the application (e.g., "Adobe Premiere Pro").
            wait: If True, wait for the app to launch.
            
        Returns:
            Tuple of (success, message).
        """
        if wait:
            script = f'''
            tell application "{app_name}"
                activate
            end tell
            delay 2
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
            end tell
            return frontApp
            '''
        else:
            script = f'tell application "{app_name}" to activate'
        
        return AppleScriptRunner.run(script)
    
    @staticmethod
    def get_frontmost_app() -> Tuple[bool, str]:
        """Get the name of the frontmost application."""
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
        end tell
        return frontApp
        '''
        return AppleScriptRunner.run(script)
    
    @staticmethod
    def click_menu_item(app_name: str, menu: str, item: str) -> Tuple[bool, str]:
        """
        Click a menu item in an application.
        
        Args:
            app_name: Application name.
            menu: Menu name (e.g., "File").
            item: Menu item name (e.g., "Save").
            
        Returns:
            Tuple of (success, message).
        """
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                click menu item "{item}" of menu "{menu}" of menu bar 1
            end tell
        end tell
        '''
        return AppleScriptRunner.run(script)


def get_tool_definition() -> Dict[str, Any]:
    """
    Get the tool definition for Claude Computer Use API.
    
    Returns:
        Dictionary matching the expected tool schema.
    """
    return {
        "type": "computer_20241022",
        "name": "computer",
        "display_width_px": pyautogui.size()[0],
        "display_height_px": pyautogui.size()[1],
        "display_number": 1
    }


if __name__ == "__main__":
    # Quick test
    controller = ComputerController()
    
    # Test screenshot
    result, image = controller.execute("screenshot")
    print(f"Screenshot: {result}, Image size: {image.size if image else 'None'}")
    
    # Test cursor position
    result, _ = controller.execute("cursor_position")
    print(f"Cursor: {result}")
    
    # Test AppleScript
    success, app = AppleScriptRunner.get_frontmost_app()
    print(f"Frontmost app: {app}")

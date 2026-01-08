"""
Screen capture and display management module.

Handles screenshot capture and screen dimension queries using PyAutoGUI.
"""

import base64
import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import pyautogui
from PIL import Image

# Disable PyAutoGUI failsafe (move mouse to corner to abort)
# Enable this in production for safety
pyautogui.FAILSAFE = True

# Default screenshot directory
DEFAULT_SCREENSHOT_DIR = Path("./screenshots")


class ScreenCapture:
    """
    Handles screen capture operations for Computer Use API.
    
    Provides methods to:
    - Capture full screen screenshots
    - Get screen dimensions
    - Save and encode screenshots for API transmission
    """
    
    def __init__(
        self,
        screenshot_dir: Optional[Path] = None,
        quality: int = 85
    ):
        """
        Initialize screen capture.
        
        Args:
            screenshot_dir: Directory to save screenshots. Defaults to ./screenshots
            quality: JPEG quality (1-100). Lower = smaller files.
        """
        self.screenshot_dir = screenshot_dir or DEFAULT_SCREENSHOT_DIR
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.quality = quality
        self._screen_size: Optional[Tuple[int, int]] = None
    
    @property
    def screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions (width, height)."""
        if self._screen_size is None:
            self._screen_size = pyautogui.size()
        return self._screen_size
    
    @property
    def width(self) -> int:
        """Get screen width in pixels."""
        return self.screen_size[0]
    
    @property
    def height(self) -> int:
        """Get screen height in pixels."""
        return self.screen_size[1]
    
    def capture(self, save: bool = True) -> Image.Image:
        """
        Capture a screenshot of the entire screen.
        
        Args:
            save: If True, save the screenshot to disk.
            
        Returns:
            PIL Image object of the screenshot.
        """
        screenshot = pyautogui.screenshot()
        
        if save:
            self.save(screenshot)
        
        return screenshot
    
    def save(self, image: Image.Image, filename: Optional[str] = None) -> Path:
        """
        Save a screenshot to disk.
        
        Args:
            image: PIL Image to save.
            filename: Optional filename. Defaults to timestamp-based name.
            
        Returns:
            Path to the saved file.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"screenshot_{timestamp}.png"
        
        filepath = self.screenshot_dir / filename
        image.save(filepath, optimize=True)
        
        return filepath
    
    def to_base64(self, image: Image.Image) -> str:
        """
        Convert a PIL Image to base64-encoded PNG string.
        
        This format is required by the Anthropic Computer Use API.
        
        Args:
            image: PIL Image to encode.
            
        Returns:
            Base64-encoded PNG string.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG", optimize=True)
        buffer.seek(0)
        return base64.standard_b64encode(buffer.read()).decode("utf-8")
    
    def capture_base64(self, save: bool = True) -> Tuple[str, Image.Image]:
        """
        Capture screenshot and return as base64 for API.
        
        Args:
            save: If True, also save the screenshot to disk.
            
        Returns:
            Tuple of (base64_string, PIL Image).
        """
        image = self.capture(save=save)
        base64_data = self.to_base64(image)
        return base64_data, image
    
    def get_display_info(self) -> dict:
        """
        Get information about the display configuration.
        
        Returns:
            Dictionary with display information.
        """
        width, height = self.screen_size
        return {
            "width": width,
            "height": height,
            "display_number": 1,  # Primary display
            "display_prefix": "display",
        }


def get_screen_info() -> dict:
    """
    Quick helper to get screen information.
    
    Returns:
        Dictionary with width, height, and other display info.
    """
    capture = ScreenCapture()
    return capture.get_display_info()


if __name__ == "__main__":
    # Quick test
    print("Screen Info:", get_screen_info())
    
    capture = ScreenCapture()
    image = capture.capture(save=True)
    print(f"Screenshot saved. Size: {image.size}")
    
    b64 = capture.to_base64(image)
    print(f"Base64 length: {len(b64)} characters")

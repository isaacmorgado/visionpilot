"""
Backend abstraction layer for computer control.

Provides pluggable backends for different automation approaches:
- PyAutoGUI: Cross-platform, requires foreground focus
- macOS Native: Background operation using Quartz/ScreenCaptureKit/CGEvent
"""

from .abstract import AbstractBackend, BackendCapabilities
from .factory import create_backend, get_available_backends
from .pyautogui_backend import PyAutoGUIBackend

__all__ = [
    "AbstractBackend",
    "BackendCapabilities",
    "PyAutoGUIBackend",
    "create_backend",
    "get_available_backends",
]

"""
Backend factory for creating and selecting computer control backends.

Handles auto-detection of the best available backend based on:
- Operating system
- Available dependencies
- User preferences
"""

import platform
from typing import Dict, List, Optional

from .abstract import AbstractBackend, BackendType
from .pyautogui_backend import PyAutoGUIBackend


def get_available_backends() -> List[str]:
    """
    Get list of available backends on current system.

    Returns:
        List of backend names that can be used (e.g., ["pyautogui", "macos"]).
    """
    available = []

    # PyAutoGUI is always available (cross-platform)
    try:
        import pyautogui

        available.append("pyautogui")
    except ImportError:
        pass

    # macOS native backend (requires PyObjC)
    if platform.system() == "Darwin":
        try:
            import Quartz
            import Cocoa

            available.append("macos")
        except ImportError:
            pass

    return available


def get_backend_info() -> Dict[str, Dict]:
    """
    Get information about all backends.

    Returns:
        Dictionary mapping backend names to their info (name, platform, capabilities).
    """
    info = {
        "pyautogui": {
            "name": "PyAutoGUI",
            "platform": "any",
            "background": False,
            "performance": "1.0x (baseline)",
            "requires": ["pyautogui"],
        },
        "macos": {
            "name": "macOS Native",
            "platform": "macOS",
            "background": True,
            "performance": "15-30x",
            "requires": ["pyobjc-framework-Quartz", "pyobjc-framework-CoreGraphics"],
        },
    }
    return info


def auto_select_backend() -> str:
    """
    Automatically select the best backend for current system.

    Selection priority:
    1. macOS native (if on macOS and dependencies available)
    2. PyAutoGUI (fallback, cross-platform)

    Returns:
        Backend name to use (e.g., "macos" or "pyautogui").

    Raises:
        RuntimeError: If no backends are available.
    """
    available = get_available_backends()

    if not available:
        raise RuntimeError(
            "No backends available! Install PyAutoGUI: pip install pyautogui"
        )

    # Prefer macOS native backend for better performance
    if "macos" in available:
        return "macos"

    # Fallback to PyAutoGUI
    if "pyautogui" in available:
        return "pyautogui"

    # Should never reach here, but handle it
    return available[0]


def create_backend(
    backend_type: Optional[str] = None, action_delay: float = 0.5, **kwargs
) -> AbstractBackend:
    """
    Create a backend instance.

    Args:
        backend_type: Backend to use ("auto", "pyautogui", "macos").
                     If None or "auto", auto-selects best backend.
        action_delay: Delay between actions in seconds.
        **kwargs: Additional backend-specific arguments.

    Returns:
        Initialized backend instance.

    Raises:
        ValueError: If backend_type is invalid or not available.
        RuntimeError: If no backends are available.

    Examples:
        >>> # Auto-select best backend
        >>> backend = create_backend()

        >>> # Explicitly use PyAutoGUI
        >>> backend = create_backend("pyautogui")

        >>> # Use macOS native (15-30x faster)
        >>> backend = create_backend("macos")
    """
    # Auto-select if not specified
    if backend_type is None or backend_type == BackendType.AUTO.value:
        backend_type = auto_select_backend()

    # Normalize backend type
    backend_type = backend_type.lower().strip()

    # Check if available
    available = get_available_backends()
    if backend_type not in available:
        available_str = ", ".join(available) if available else "None"
        raise ValueError(
            f"Backend '{backend_type}' not available. Available backends: {available_str}"
        )

    # Create backend instance
    if backend_type == "pyautogui":
        return PyAutoGUIBackend(action_delay=action_delay, **kwargs)

    elif backend_type == "macos":
        # Import macOS backend only when needed (fails on non-macOS)
        try:
            from .macos_backend import MacOSBackend

            return MacOSBackend(action_delay=action_delay, **kwargs)
        except ImportError as e:
            raise ValueError(
                "macOS backend requires PyObjC. Install with: "
                "pip install pyobjc-framework-Quartz pyobjc-framework-CoreGraphics"
            ) from e

    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


def print_backend_comparison():
    """
    Print a comparison table of available backends.

    Useful for CLI help and documentation.
    """
    from rich.console import Console
    from rich.table import Table

    console = Console()
    table = Table(title="Available Backends")

    table.add_column("Backend", style="cyan")
    table.add_column("Platform", style="yellow")
    table.add_column("Background", style="green")
    table.add_column("Performance", style="magenta")
    table.add_column("Available", style="green")

    available = get_available_backends()
    info = get_backend_info()

    for backend_name, backend_info in info.items():
        is_available = "✓" if backend_name in available else "✗"
        bg_support = "✓" if backend_info["background"] else "✗"

        table.add_row(
            backend_info["name"],
            backend_info["platform"],
            bg_support,
            backend_info["performance"],
            is_available,
        )

    console.print(table)

    # Show selected backend
    if available:
        selected = auto_select_backend()
        selected_info = info.get(selected, {})
        console.print(
            f"\n[bold]Auto-selected:[/bold] {selected_info.get('name', selected)}"
        )
    else:
        console.print("\n[red]⚠ No backends available![/red]")
        console.print("Install PyAutoGUI: pip install pyautogui")


if __name__ == "__main__":
    # Test backend detection and creation
    print("Detecting available backends...")
    print_backend_comparison()

    print("\nCreating auto-selected backend...")
    try:
        backend = create_backend()
        caps = backend.get_capabilities()
        print(f"Created: {caps.name}")
        print(f"  Background capture: {caps.background_capture}")
        print(f"  Background input: {caps.background_input}")
        print(f"  Performance: {caps.performance_multiplier}x")
    except Exception as e:
        print(f"Error: {e}")

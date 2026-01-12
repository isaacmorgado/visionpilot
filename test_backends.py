#!/usr/bin/env python3
"""
Test script for backend abstraction layer.
Tests backend detection, creation, and basic operations.
"""

import platform

# Test backend detection
print("=== Testing Backend Detection ===\n")

# Test PyAutoGUI availability
try:
    import pyautogui

    print("✓ PyAutoGUI available")
    pyautogui_available = True
except ImportError:
    print("✗ PyAutoGUI not available")
    pyautogui_available = False

# Test macOS dependencies
if platform.system() == "Darwin":
    try:
        import Quartz
        import Cocoa

        print("✓ PyObjC (macOS backend) available")
        macos_available = True
    except ImportError:
        print("✗ PyObjC not available (install: pip install pyobjc-framework-Quartz)")
        macos_available = False
else:
    print(f"✗ macOS backend not available (running on {platform.system()})")
    macos_available = False

print("\n=== Testing Backend Creation ===\n")

# Import after checking dependencies
try:
    from src.backends.factory import (
        create_backend,
        get_available_backends,
        auto_select_backend,
    )

    # Get available backends
    available = get_available_backends()
    print(f"Available backends: {available}")

    # Auto-select best backend
    selected = auto_select_backend()
    print(f"Auto-selected: {selected}")

    # Create backend
    print(f"\nCreating '{selected}' backend...")
    backend = create_backend(selected)

    caps = backend.get_capabilities()
    print(f"\nBackend: {caps.name}")
    print(f"  Platform: {caps.platform}")
    print(f"  Background capture: {caps.background_capture}")
    print(f"  Background input: {caps.background_input}")
    print(f"  Performance: {caps.performance_multiplier}x")
    print(f"  Requires accessibility: {caps.requires_accessibility}")
    print(f"  Requires screen recording: {caps.requires_screen_recording}")

    # Test basic operation
    print("\n=== Testing Basic Operations ===\n")

    # Test screen size
    width, height = backend.get_screen_size()
    print(f"✓ Screen size: {width}x{height}")

    # Test cursor position
    msg, (x, y) = backend.cursor_position()
    print(f"✓ Cursor position: ({x}, {y})")

    # Test action counter
    print(f"✓ Actions performed: {backend.action_count}")

    print("\n=== Test Complete ===")
    print("Backend abstraction layer is working correctly!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback

    traceback.print_exc()

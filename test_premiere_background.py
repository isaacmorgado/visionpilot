#!/usr/bin/env python3
"""
Test Premiere Pro Plugin with BACKGROUND Automation

This script automates Premiere Pro WITHOUT taking control of your mouse/keyboard.
You can continue working while it runs in the background!

Uses VisionPilot Week 2 background automation features:
- capture_window_by_pid() - Capture without activating
- send_click_to_pid() - Click without moving your mouse
- send_key_to_pid() - Type without using your keyboard
"""

import sys
import time
import subprocess
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.context import AutomationContext


def find_premiere_pro():
    """Find Premiere Pro process."""
    try:
        result = subprocess.run(
            ["pgrep", "-f", "Adobe Premiere Pro"], capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().split()[0])
            print(f"✓ Found Premiere Pro (PID: {pid})")
            return pid
        else:
            print("✗ Premiere Pro not running")
            return None
    except Exception as e:
        print(f"✗ Error finding Premiere Pro: {e}")
        return None


def test_premiere_background():
    """Test Premiere Pro plugin with BACKGROUND automation."""
    print("=" * 70)
    print("PREMIERE PRO PLUGIN TEST - BACKGROUND MODE")
    print("=" * 70)
    print()
    print("  ✨ This test runs IN THE BACKGROUND")
    print("  ✨ You can continue using your mouse and keyboard!")
    print("  ✨ Automation events are sent directly to Premiere Pro")
    print()
    print("=" * 70)

    # Danny's credentials
    DANNY_LICENSE = "SPLICE-Y2Q9-6G9G-MFQE"

    # Find Premiere Pro
    premiere_pid = find_premiere_pro()
    if not premiere_pid:
        print("\n✗ Premiere Pro must be running for background automation")
        print("  Please launch Premiere Pro and try again")
        return False

    # Create automation context with macOS backend
    print("\nInitializing VisionPilot AutomationContext (BACKGROUND MODE)...")
    with AutomationContext(
        backend="macos",
        action_delay=0.0,  # No delay needed for background operations
        cleanup_on_close=False,  # Preserve screenshots
        metadata={
            "task": "premiere_background_test",
            "user": "danny_isakov",
            "license": DANNY_LICENSE,
        },
    ) as ctx:
        print(f"✓ Context initialized: {ctx.context_id}")
        print(f"  Backend: {ctx.backend_name}")
        print(f"  Screenshot dir: {ctx.screenshot_dir}")
        print()

        # Step 1: Background screenshot
        print("-" * 70)
        print("Step 1: Capture Premiere Pro window (no activation)")
        print("-" * 70)
        print(f"  Capturing window for PID {premiere_pid}")
        print("  Your screen won't flash - this is background capture!")
        print()

        image = ctx.capture_window_by_pid(premiere_pid)
        if image:
            print(f"✓ Background screenshot captured: {image.size}")
            screenshot_path = (
                ctx.screenshot_dir / f"bg_initial_{int(time.time() * 1000000)}.png"
            )
            image.save(screenshot_path)
            print(f"  Saved to: {screenshot_path.name}")
        else:
            print("⚠️  PID capture failed - falling back to regular screenshot")
            print(
                "  (This is normal if window is minimized or background capture isn't available)"
            )
            msg, image = ctx.screenshot()
            if image:
                print(f"✓ Fallback screenshot captured: {image.size}")
            else:
                print("✗ All capture methods failed")
                return False

        time.sleep(1)

        # Step 2: Click Login button (BACKGROUND)
        print()
        print("-" * 70)
        print("Step 2: Click Login button (background click)")
        print("-" * 70)
        print("  ⚡ YOUR MOUSE WON'T MOVE - watch Premiere Pro instead!")
        print()

        # Correct coordinates from screenshot analysis
        login_button_x = 1270
        login_button_y = 100

        print(
            f"  Sending background click to PID {premiere_pid} at ({login_button_x}, {login_button_y})"
        )
        success = ctx.send_click_to_pid(premiere_pid, login_button_x, login_button_y)
        if success:
            print("  ✓ Background click sent!")
        else:
            print("  ⚠️  Background click failed, using fallback")
            ctx.click(login_button_x, login_button_y)
        time.sleep(2)

        # Capture result
        image = ctx.capture_window_by_pid(premiere_pid)
        if image:
            screenshot_path = (
                ctx.screenshot_dir / f"bg_after_click_{int(time.time() * 1000000)}.png"
            )
            image.save(screenshot_path)
            print(f"  Captured: {screenshot_path.name}")

        # Step 3: Type license key (BACKGROUND)
        print()
        print("-" * 70)
        print("Step 3: Enter license key (background typing)")
        print("-" * 70)
        print("  ⚡ YOUR KEYBOARD WON'T TYPE - watch Premiere Pro instead!")
        print()

        time.sleep(1)  # Wait for modal

        print(f"  Typing license key: {DANNY_LICENSE}")
        ctx.send_key_to_pid(premiere_pid, DANNY_LICENSE)
        print("  ✓ Background typing sent!")
        time.sleep(1)

        # Capture result
        image = ctx.capture_window_by_pid(premiere_pid)
        if image:
            screenshot_path = (
                ctx.screenshot_dir / f"bg_after_type_{int(time.time() * 1000000)}.png"
            )
            image.save(screenshot_path)
            print(f"  Captured: {screenshot_path.name}")

        # Step 4: Submit (BACKGROUND)
        print()
        print("-" * 70)
        print("Step 4: Submit login (press Enter)")
        print("-" * 70)

        print("  Sending Enter key")
        ctx.send_key_to_pid(premiere_pid, "return")
        print("  ✓ Background Enter key sent!")
        time.sleep(3)  # Wait for authentication

        # Final capture
        print()
        print("-" * 70)
        print("Step 5: Verify login success")
        print("-" * 70)

        image = ctx.capture_window_by_pid(premiere_pid)
        if image:
            screenshot_path = (
                ctx.screenshot_dir / f"bg_final_{int(time.time() * 1000000)}.png"
            )
            image.save(screenshot_path)
            print(f"✓ Final screenshot: {screenshot_path.name}")

        # Get statistics
        stats = ctx.get_stats()

        print()
        print("=" * 70)
        print("BACKGROUND TEST COMPLETE")
        print("=" * 70)
        print()
        print("Context Statistics:")
        print(f"  Actions performed: {stats['action_count']}")
        print(f"  Screenshots taken: {stats['screenshot_count']}")
        print(f"  Backend: {stats['backend']}")
        print()
        print("✅ All screenshots saved to:")
        print(f"   {ctx.screenshot_dir}")
        print()
        print("📋 You can now:")
        print("   1. Check Premiere Pro to see if login succeeded")
        print("   2. Review screenshots in the directory above")
        print("   3. Continue using your computer - this ran in background!")
        print()

        return True


if __name__ == "__main__":
    try:
        success = test_premiere_background()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✋ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

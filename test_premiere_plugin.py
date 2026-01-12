#!/usr/bin/env python3
"""
Test Premiere Pro Plugin with VisionPilot AutomationContext

Uses the new Week 3+ implementation to test the SPLICE plugin
with Danny's beta credentials.
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


def launch_premiere_pro():
    """Launch Premiere Pro."""
    print("\nLaunching Premiere Pro...")
    try:
        subprocess.Popen(
            [
                "/Applications/Adobe Premiere Pro 2025/Adobe Premiere Pro 2025.app/Contents/MacOS/Adobe Premiere Pro 2025"
            ]
        )
        print("✓ Launched Premiere Pro")
        print("  Waiting 10 seconds for startup...")
        time.sleep(10)
        return find_premiere_pro()
    except Exception as e:
        print(f"✗ Failed to launch: {e}")
        return None


def activate_premiere_pro():
    """Activate Premiere Pro window using AppleScript."""
    print("\nActivating Premiere Pro window...")
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "Adobe Premiere Pro 2025" to activate',
            ],
            check=True,
        )
        print("✓ Premiere Pro activated")
        time.sleep(2)  # Wait for window to come to foreground
        return True
    except Exception as e:
        print(f"✗ Failed to activate: {e}")
        return False


def test_premiere_plugin():
    """Test Premiere Pro plugin with VisionPilot."""
    print("=" * 60)
    print("PREMIERE PRO PLUGIN TEST (VisionPilot)")
    print("=" * 60)

    # Danny's credentials
    DANNY_LICENSE = "SPLICE-Y2Q9-6G9G-MFQE"

    # Find or launch Premiere Pro
    premiere_pid = find_premiere_pro()
    if not premiere_pid:
        print("\nPremiere Pro not running. Attempting to launch...")
        premiere_pid = launch_premiere_pro()
        if not premiere_pid:
            print("\n✗ Cannot proceed without Premiere Pro")
            return False

    # Activate Premiere Pro window
    if not activate_premiere_pro():
        print("\n✗ Cannot proceed without activating Premiere Pro")
        return False

    # Create automation context with macOS backend for maximum performance
    print("\nInitializing VisionPilot AutomationContext...")
    with AutomationContext(
        backend="macos",
        action_delay=0.5,
        cleanup_on_close=False,  # Preserve screenshots for review
        metadata={
            "task": "premiere_plugin_test",
            "user": "danny_isakov",
            "license": DANNY_LICENSE,
        },
    ) as ctx:
        print(f"✓ Context initialized: {ctx.context_id}")
        print(f"  Backend: {ctx.backend_name}")
        print(f"  Screenshot dir: {ctx.screenshot_dir}")

        # Step 1: Take initial screenshot
        print("\n" + "-" * 60)
        print("Step 1: Capture current state")
        print("-" * 60)
        msg, image = ctx.screenshot()
        print(f"✓ Screenshot captured: {image.size}")
        print(f"  Saved to: {ctx.screenshot_dir}")

        # Step 2: Open Extensions menu
        print("\n" + "-" * 60)
        print("Step 2: Open Window > Extensions menu")
        print("-" * 60)

        # Get screen size for positioning
        width, height = ctx.get_screen_size()
        print(f"  Screen size: {width}x{height}")

        # Click on Window menu (approximate position)
        window_menu_x = width // 2 - 200
        window_menu_y = 30

        print(f"  Clicking Window menu at ({window_menu_x}, {window_menu_y})")
        ctx.click(window_menu_x, window_menu_y)
        time.sleep(1)

        # Take screenshot to see menu
        msg, menu_image = ctx.screenshot()
        print(f"✓ Menu screenshot: {menu_image.size}")

        # Click Extensions submenu (approximate)
        extensions_x = window_menu_x
        extensions_y = window_menu_y + 100

        print(f"  Clicking Extensions at ({extensions_x}, {extensions_y})")
        ctx.click(extensions_x, extensions_y)
        time.sleep(1)

        # Step 3: Click SPLICE extension
        print("\n" + "-" * 60)
        print("Step 3: Click SPLICE extension")
        print("-" * 60)

        # SPLICE should appear in submenu
        splice_x = extensions_x + 150
        splice_y = extensions_y

        print(f"  Clicking SPLICE at ({splice_x}, {splice_y})")
        ctx.click(splice_x, splice_y)
        time.sleep(2)

        # Take screenshot to see SPLICE panel
        msg, splice_image = ctx.screenshot()
        print(f"✓ SPLICE panel screenshot: {splice_image.size}")

        # Step 4: Enter Danny's license key
        print("\n" + "-" * 60)
        print("Step 4: Enter license key and login")
        print("-" * 60)

        # Click in license key field (center-right of screen)
        license_field_x = width - 300
        license_field_y = height // 2

        print(f"  Clicking license field at ({license_field_x}, {license_field_y})")
        ctx.click(license_field_x, license_field_y)
        time.sleep(0.5)

        # Type Danny's license key
        print(f"  Typing license key: {DANNY_LICENSE}")
        ctx.type_text(DANNY_LICENSE)
        time.sleep(0.5)

        # Take screenshot to verify entry
        msg, license_entered = ctx.screenshot()
        print(f"✓ License entered screenshot: {license_entered.size}")

        # Click login button (below license field)
        login_button_x = license_field_x
        login_button_y = license_field_y + 50

        print(f"  Clicking Login button at ({login_button_x}, {login_button_y})")
        ctx.click(login_button_x, login_button_y)
        time.sleep(2)

        # Step 5: Verify login and capture final state
        print("\n" + "-" * 60)
        print("Step 5: Verify login success")
        print("-" * 60)

        msg, final_image = ctx.screenshot()
        print(f"✓ Final state screenshot: {final_image.size}")

        # Get context statistics
        stats = ctx.get_stats()

        print("\n" + "=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)
        print("\nContext Statistics:")
        print(f"  Actions performed: {stats['action_count']}")
        print(f"  Screenshots taken: {stats['screenshot_count']}")
        print(f"  Backend used: {stats['backend']}")
        print(f"  Screenshots saved to: {stats['screenshot_dir']}")

        print("\n✅ All screenshots saved to:")
        print(f"   {ctx.screenshot_dir}")

        print("\n📋 Next Steps:")
        print(f"   1. Review screenshots in {ctx.screenshot_dir}")
        print("   2. Check Premiere Pro console logs for errors")
        print("   3. Manually verify login succeeded in Premiere Pro")
        print("   4. Test UI elements in the SPLICE panel")

        return True


if __name__ == "__main__":
    try:
        success = test_premiere_plugin()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✋ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

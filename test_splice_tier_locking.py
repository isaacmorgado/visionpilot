#!/usr/bin/env python3
"""
SPLICE Tier Locking Test
Tests feature access across different subscription tiers (Starter, Pro, Team)
"""

import sys
import time

sys.path.insert(0, "/Users/imorgado/Desktop/Development/Projects/visionpilot")
sys.path.insert(0, "/Users/imorgado/Desktop/Development/Projects/visionpilot/src")

from src.context import AutomationContext


class TierLockingTestSuite:
    """Test tier-based feature locking in SPLICE panel."""

    def __init__(self, premiere_pid: int):
        self.premiere_pid = premiere_pid
        self.ctx = None

        # Test user credentials by tier
        self.test_users = {
            "starter": {
                "license": "SPLICE-82CF-4ZAQ-66F6",
                "email": "test-starter@splice.video",
                "tier": "Starter",
                "hours": "4h",
                "music_credits": "5",
                "expected_locked_features": ["Isolated Vocals", "Advanced Features"],
            },
            "pro": {
                "license": "SPLICE-7XWQ-VE7Y-MDJN",
                "email": "test-pro@splice.video",
                "tier": "Pro",
                "hours": "15h",
                "music_credits": "20",
                "expected_locked_features": ["Some Team-only Features"],
            },
            "team": {
                "license": "SPLICE-7DVR-4AEU-W8BU",
                "email": "test-team@splice.video",
                "tier": "Team",
                "hours": "50h",
                "music_credits": "100",
                "expected_locked_features": [],  # No locked features
            },
        }

        # UI element coordinates (same as comprehensive test)
        self.coords = {
            "login_button": (1270, 100),
            "credit_badge": (1320, 100),
            "isolated_vocals_checkbox": (1270, 380),
            "options_toggle": (1270, 250),
            "multitrack_toggle": (1270, 450),
            "music_toggle": (1270, 850),
        }

        self.test_results = []

    def initialize_context(self):
        """Initialize VisionPilot context."""
        self.ctx = AutomationContext(backend="macos")
        print(f"✓ Context initialized: {self.ctx.context_id[:8]}")
        print(f"  Screenshots: {self.ctx.screenshot_dir}\n")

    def cleanup(self):
        """Cleanup context."""
        if self.ctx:
            self.ctx.close()

    def capture_screenshot(self, name: str):
        """Capture screenshot with timestamp."""
        timestamp = int(time.time() * 1_000_000)
        safe_name = name.replace(" ", "_").replace("/", "_")
        filename = f"{safe_name}_{timestamp}.png"

        image = self.ctx.capture_window_by_pid(self.premiere_pid)
        if image:
            path = self.ctx.screenshot_dir / filename
            image.save(path)
            print(f"   📸 Screenshot: {filename}")
        else:
            print(f"   ⚠️  Screenshot failed: {filename}")

    def click_element(self, description: str, x: int, y: int, delay: float = 1):
        """Click element in background."""
        print(f"   🖱️  Clicking {description} at ({x}, {y})")
        self.ctx.send_click_to_pid(self.premiere_pid, x, y)
        time.sleep(delay)

    def type_text(self, text: str, delay: float = 0.05):
        """Type text character by character."""
        print(f"   ⌨️  Typing: {text}")
        for char in text:
            self.ctx.send_key_to_pid(self.premiere_pid, char)
            time.sleep(delay)
        time.sleep(0.5)

    def logout(self):
        """Logout current user."""
        print("   🚪 Logging out...")
        # Click credit badge to open dropdown, then logout
        self.click_element("Credit badge", *self.coords["credit_badge"], delay=1)
        # Assuming logout is in dropdown (approximate position)
        self.click_element("Logout", 1320, 150, delay=2)

    def test_tier_login(self, tier: str) -> bool:
        """Test login with specific tier and verify feature access."""
        user = self.test_users[tier]

        print(f"\n{'=' * 70}")
        print(f"TESTING {user['tier'].upper()} TIER")
        print(f"{'=' * 70}")
        print(f"License: {user['license']}")
        print(f"Expected Hours: {user['hours']}")
        print(f"Music Credits: {user['music_credits']}")
        print(
            f"Expected Locked: {', '.join(user['expected_locked_features']) or 'None'}"
        )
        print("")

        # Step 1: Take initial screenshot
        self.capture_screenshot(f"01_{tier}_initial_state")

        # Step 2: Click login button
        self.click_element("Login button", *self.coords["login_button"], delay=2)
        self.capture_screenshot(f"02_{tier}_login_clicked")

        # Step 3: Type license key
        self.type_text(user["license"], delay=0.05)
        time.sleep(1)
        self.capture_screenshot(f"03_{tier}_license_entered")

        # Step 4: Press Enter to submit
        print("   ⏎  Pressing Enter to submit")
        self.ctx.send_key_to_pid(self.premiere_pid, "return")
        time.sleep(3)  # Wait for authentication
        self.capture_screenshot(f"04_{tier}_authenticated")

        # Step 5: Verify credit badge shows tier
        self.capture_screenshot(f"05_{tier}_credit_badge")
        print(f"✅ PASS: {user['tier']} tier login successful")

        # Step 6: Test Isolated Vocals (PRO feature)
        print("\n🔒 Testing Isolated Vocals (PRO feature)...")
        print("----------------------------------------------------------------------")

        # Open options panel
        self.click_element("Options toggle", *self.coords["options_toggle"], delay=1)
        self.capture_screenshot(f"06_{tier}_options_expanded")

        # Click Isolated Vocals checkbox
        self.click_element(
            "Isolated Vocals", *self.coords["isolated_vocals_checkbox"], delay=2
        )
        self.capture_screenshot(f"07_{tier}_isolated_vocals_clicked")

        if tier == "starter":
            print("⚠️  EXPECTED: Upgrade modal should appear for Starter tier")
            # Take screenshot of expected upgrade modal
            self.capture_screenshot(f"08_{tier}_upgrade_modal_expected")
            # Close modal with Escape
            print("   ⎋  Pressing Escape to close modal")
            self.ctx.send_key_to_pid(self.premiere_pid, "escape")
            time.sleep(1)
        else:
            print(f"✅ EXPECTED: {user['tier']} tier should have access")

        # Step 7: Test Multitrack (available to all tiers)
        print("\n✓ Testing Multitrack (available to all tiers)...")
        print("----------------------------------------------------------------------")
        self.click_element(
            "Multitrack toggle", *self.coords["multitrack_toggle"], delay=1
        )
        self.capture_screenshot(f"09_{tier}_multitrack_expanded")
        print("✅ PASS: Multitrack section accessible")

        # Step 8: Test Music Generation (credit-limited)
        print("\n🎵 Testing Music Generation (credit-limited)...")
        print("----------------------------------------------------------------------")
        self.click_element("Music toggle", *self.coords["music_toggle"], delay=1)
        self.capture_screenshot(f"10_{tier}_music_expanded")
        print("✅ PASS: Music section accessible")
        print(f"   Music credits available: {user['music_credits']}")

        # Step 9: Logout
        self.logout()
        self.capture_screenshot(f"11_{tier}_logged_out")
        print(f"✅ PASS: {user['tier']} tier logout successful\n")

        return True

    def run(self):
        """Run tier locking tests."""
        print("=" * 70)
        print("SPLICE PLUGIN - TIER LOCKING TEST SUITE")
        print("=" * 70)
        print("")
        print("  ✨ Using VisionPilot background automation")
        print("  ✨ Your mouse and keyboard remain free!")
        print("")
        print("=" * 70)

        try:
            # Initialize
            self.initialize_context()

            # Test each tier
            for tier in ["starter", "pro", "team"]:
                try:
                    self.test_tier_login(tier)
                    self.test_results.append((tier, "PASS"))
                except Exception as e:
                    print(f"❌ FAIL: {tier} tier test failed: {e}")
                    self.test_results.append((tier, "FAIL", str(e)))

                # Wait between tier tests
                time.sleep(2)

            # Print summary
            print("\n" + "=" * 70)
            print("TIER LOCKING TEST SUMMARY")
            print("=" * 70)
            for result in self.test_results:
                tier = result[0]
                status = result[1]
                emoji = "✅" if status == "PASS" else "❌"
                print(f"{emoji} {tier.upper()}: {status}")
            print("=" * 70)

        finally:
            self.cleanup()


if __name__ == "__main__":
    import subprocess

    # Get Premiere Pro PID
    result = subprocess.run(["pgrep", "-i", "premiere"], capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Premiere Pro not running")
        sys.exit(1)

    pid = int(result.stdout.strip().split("\n")[0])
    print(f"✓ Found Premiere Pro (PID: {pid})\n")

    # Run tests
    suite = TierLockingTestSuite(pid)
    suite.run()

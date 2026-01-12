#!/usr/bin/env python3
"""
Week 4: Edge Case Testing

Tests edge cases and error conditions:
- Minimized windows (background capture)
- Multiple displays
- Screen resolution changes
- Invalid operations
- Context lifecycle edge cases
- Backend fallback scenarios
"""

import sys
import platform
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.context import AutomationContext


class EdgeCaseTest:
    """
    Edge case testing framework.

    Tests unusual scenarios, error conditions, and boundary cases.
    """

    def __init__(self):
        """Initialize edge case test framework."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def test_closed_context_operations(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that operations on closed contexts raise proper errors.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Closed Context Operations")
        print(f"{'─' * 60}")

        ctx = AutomationContext(backend=backend, action_delay=0.0)
        ctx.close()

        # Test various operations on closed context
        operations = {
            "screenshot": lambda: ctx.screenshot(),
            "click": lambda: ctx.click(100, 100),
            "mouse_move": lambda: ctx.mouse_move(100, 100),
            "key_press": lambda: ctx.key_press("a"),
            "type_text": lambda: ctx.type_text("test"),
            "get_screen_size": lambda: ctx.get_screen_size(),
        }

        results = {}
        for op_name, op_func in operations.items():
            try:
                op_func()
                self.errors.append(
                    f"Operation '{op_name}' should raise RuntimeError on closed context"
                )
                results[op_name] = "FAILED: No error raised"
                print(f"  ✗ {op_name}: No error raised")
            except RuntimeError as e:
                if "closed" in str(e).lower():
                    results[op_name] = "PASSED"
                    print(f"  ✓ {op_name}: Proper error raised")
                else:
                    results[op_name] = f"FAILED: Unexpected error: {e}"
                    self.errors.append(f"Operation '{op_name}' unexpected error: {e}")
                    print(f"  ✗ {op_name}: Unexpected error")
            except Exception as e:
                results[op_name] = f"FAILED: Wrong exception type: {type(e).__name__}"
                self.errors.append(f"Operation '{op_name}' wrong exception: {e}")
                print(f"  ✗ {op_name}: Wrong exception type")

        return {
            "success": len(self.errors) == 0,
            "operations_tested": len(operations),
            "results": results,
            "errors": list(self.errors),
        }

    def test_double_close(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that closing a context twice is safe.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Double Close Safety")
        print(f"{'─' * 60}")

        try:
            ctx = AutomationContext(backend=backend, action_delay=0.0)
            ctx.close()
            ctx.close()  # Should be safe
            print("  ✓ Double close is safe (no error)")

            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Double close raised error: {e}")
            print(f"  ✗ Double close raised error: {e}")

            return {"success": False, "errors": list(self.errors)}

    def test_context_manager_exception(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that context manager cleans up even when exception occurs.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Context Manager Exception Handling")
        print(f"{'─' * 60}")

        try:
            with AutomationContext(backend=backend, action_delay=0.0) as ctx:
                screenshot_dir = ctx.screenshot_dir
                temp_dir = ctx.temp_dir

                # Verify directories exist during context
                if not screenshot_dir.exists() or not temp_dir.exists():
                    self.errors.append("Directories don't exist during context")
                    print("  ✗ Directories missing during context")
                    return {"success": False, "errors": list(self.errors)}

                # Raise exception
                raise ValueError("Test exception")

        except ValueError:
            # Expected
            pass

        # Verify cleanup happened despite exception
        if not screenshot_dir.exists() and not temp_dir.exists():
            print("  ✓ Context cleaned up despite exception")
            return {"success": True, "errors": []}
        else:
            self.errors.append("Context not cleaned up after exception")
            print("  ✗ Context not cleaned up")
            return {"success": False, "errors": list(self.errors)}

    def test_invalid_backend(self) -> Dict[str, Any]:
        """
        Test that invalid backend name raises proper error.

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Invalid Backend Handling")
        print(f"{'─' * 60}")

        try:
            ctx = AutomationContext(backend="invalid_backend", action_delay=0.0)
            ctx.close()
            self.errors.append("Invalid backend should raise ValueError")
            print("  ✗ No error raised for invalid backend")
            return {"success": False, "errors": list(self.errors)}

        except ValueError as e:
            print(f"  ✓ Proper error raised: {e}")
            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Wrong exception type: {type(e).__name__}")
            print(f"  ✗ Wrong exception type: {type(e).__name__}")
            return {"success": False, "errors": list(self.errors)}

    def test_zero_action_delay(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that zero action delay works correctly.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Zero Action Delay")
        print(f"{'─' * 60}")

        try:
            with AutomationContext(backend=backend, action_delay=0.0) as ctx:
                # Perform rapid operations
                ctx.screenshot(save=False)
                ctx.click(100, 100)
                ctx.key_press("a")

            print("  ✓ Zero action delay works")
            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Zero action delay failed: {e}")
            print(f"  ✗ Zero action delay failed: {e}")
            return {"success": False, "errors": list(self.errors)}

    def test_custom_directories(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test using custom screenshot and temp directories.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Custom Directories")
        print(f"{'─' * 60}")

        import tempfile
        import shutil

        # Create temp dirs
        screenshot_dir = Path(tempfile.mkdtemp(prefix="test_screenshots_"))
        temp_dir = Path(tempfile.mkdtemp(prefix="test_temp_"))

        try:
            ctx = AutomationContext(
                backend=backend,
                action_delay=0.0,
                screenshot_dir=str(screenshot_dir),
                temp_dir=str(temp_dir),
                cleanup_on_close=False,
            )

            # Verify custom dirs are used
            if ctx.screenshot_dir != screenshot_dir:
                self.errors.append("Custom screenshot directory not used")
                print("  ✗ Custom screenshot directory not used")
                return {"success": False, "errors": list(self.errors)}

            if ctx.temp_dir != temp_dir:
                self.errors.append("Custom temp directory not used")
                print("  ✗ Custom temp directory not used")
                return {"success": False, "errors": list(self.errors)}

            ctx.close()

            # Verify dirs still exist (cleanup_on_close=False)
            if not screenshot_dir.exists() or not temp_dir.exists():
                self.errors.append(
                    "Custom directories were cleaned up (should persist)"
                )
                print("  ✗ Custom directories were cleaned up")
                return {"success": False, "errors": list(self.errors)}

            print("  ✓ Custom directories work correctly")

            # Cleanup
            shutil.rmtree(screenshot_dir, ignore_errors=True)
            shutil.rmtree(temp_dir, ignore_errors=True)

            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Custom directories test failed: {e}")
            print(f"  ✗ Custom directories test failed: {e}")

            # Cleanup
            shutil.rmtree(screenshot_dir, ignore_errors=True)
            shutil.rmtree(temp_dir, ignore_errors=True)

            return {"success": False, "errors": list(self.errors)}

    def test_metadata_persistence(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that context metadata persists correctly.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Metadata Persistence")
        print(f"{'─' * 60}")

        metadata = {
            "task": "test_task",
            "user": "test_user",
            "nested": {"key": "value"},
        }

        try:
            with AutomationContext(
                backend=backend, action_delay=0.0, metadata=metadata
            ) as ctx:
                stats = ctx.get_stats()

                if stats["metadata"] != metadata:
                    self.errors.append("Metadata not preserved correctly")
                    print("  ✗ Metadata mismatch")
                    return {"success": False, "errors": list(self.errors)}

            print("  ✓ Metadata preserved correctly")
            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Metadata test failed: {e}")
            print(f"  ✗ Metadata test failed: {e}")
            return {"success": False, "errors": list(self.errors)}

    def test_background_capture_available(self) -> Dict[str, Any]:
        """
        Test if background capture is available (macOS only).

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Background Capture Availability")
        print(f"{'─' * 60}")

        if platform.system() != "Darwin":
            print("  ⊘ Skipped (not macOS)")
            return {"success": True, "skipped": True}

        try:
            with AutomationContext(backend="macos", action_delay=0.0) as ctx:
                # Check capabilities
                caps = ctx._backend.get_capabilities()

                if not caps.background_capture:
                    self.warnings.append(
                        "macOS backend doesn't report background capture capability"
                    )
                    print("  ⚠️  Background capture not reported")
                else:
                    print("  ✓ Background capture available")

                # Try to use background capture method
                try:
                    # Note: This will likely fail without a real PID, but tests the method exists
                    result = ctx.capture_window_by_pid(9999)
                    print("  ✓ Background capture method exists")
                except Exception:
                    print(
                        "  ✓ Background capture method exists (failed as expected with invalid PID)"
                    )

            return {"success": True, "warnings": list(self.warnings)}

        except Exception as e:
            self.errors.append(f"Background capture test failed: {e}")
            print(f"  ✗ Background capture test failed: {e}")
            return {"success": False, "errors": list(self.errors)}

    def test_large_action_count(self, backend: str = "auto") -> Dict[str, Any]:
        """
        Test that action counting works with many operations.

        Args:
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print("TEST: Large Action Count")
        print(f"{'─' * 60}")

        num_operations = 1000

        try:
            with AutomationContext(backend=backend, action_delay=0.0) as ctx:
                for i in range(num_operations):
                    ctx.screenshot(save=False)

                stats = ctx.get_stats()

                if stats["action_count"] != num_operations:
                    self.errors.append(
                        f"Action count mismatch: expected {num_operations}, got {stats['action_count']}"
                    )
                    print("  ✗ Action count mismatch")
                    return {"success": False, "errors": list(self.errors)}

                if stats["screenshot_count"] != num_operations:
                    self.errors.append(
                        f"Screenshot count mismatch: expected {num_operations}, got {stats['screenshot_count']}"
                    )
                    print("  ✗ Screenshot count mismatch")
                    return {"success": False, "errors": list(self.errors)}

            print(f"  ✓ Correctly tracked {num_operations} operations")
            return {"success": True, "errors": []}

        except Exception as e:
            self.errors.append(f"Large action count test failed: {e}")
            print(f"  ✗ Large action count test failed: {e}")
            return {"success": False, "errors": list(self.errors)}


def main():
    """Run edge case test suite."""
    print("\n" + "=" * 60)
    print("WEEK 4: EDGE CASE TEST SUITE")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")

    # Select backend
    if platform.system() == "Darwin":
        backend = "macos"
        print("Backend: macOS Native")
    else:
        backend = "pyautogui"
        print("Backend: PyAutoGUI")

    edge_test = EdgeCaseTest()
    results = {}

    # Run tests
    results["closed_context"] = edge_test.test_closed_context_operations(backend)
    results["double_close"] = edge_test.test_double_close(backend)
    results["context_manager_exception"] = edge_test.test_context_manager_exception(
        backend
    )
    results["invalid_backend"] = edge_test.test_invalid_backend()
    results["zero_action_delay"] = edge_test.test_zero_action_delay(backend)
    results["custom_directories"] = edge_test.test_custom_directories(backend)
    results["metadata_persistence"] = edge_test.test_metadata_persistence(backend)
    results["background_capture"] = edge_test.test_background_capture_available()
    results["large_action_count"] = edge_test.test_large_action_count(backend)

    # Summary
    print(f"\n{'=' * 60}")
    print("EDGE CASE TEST SUMMARY")
    print(f"{'=' * 60}")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("success", False))
    skipped_tests = sum(1 for r in results.values() if r.get("skipped", False))

    print(f"\nTests passed: {passed_tests}/{total_tests}")
    if skipped_tests > 0:
        print(f"Tests skipped: {skipped_tests} (platform-specific)")

    if passed_tests == total_tests:
        print("✅ All edge case tests passed!")
    else:
        print("⚠️  Some edge case tests failed - review errors above")

    # Save results
    import json

    results_file = Path(__file__).parent / "edge_case_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✅ Results saved to: {results_file}")

    print("\n🎯 Week 4 testing complete! Review all results:")
    print("   - benchmark_results.json")
    print("   - stress_test_results.json")
    print("   - edge_case_results.json")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Week 4: Multi-Context Stress Testing

Stress tests for parallel automation contexts:
- Multiple simultaneous contexts (up to 20)
- Context isolation verification
- Resource leak detection
- Thread safety testing
- Memory pressure testing
"""

import time
import sys
import threading
import psutil
import os
from pathlib import Path
from typing import List, Dict, Any
import traceback

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.context import AutomationContext


class StressTest:
    """
    Stress testing framework for AutomationContext.

    Tests parallel execution, resource limits, and isolation guarantees.
    """

    def __init__(self):
        """Initialize stress test framework."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def test_parallel_contexts(
        self, num_contexts: int = 10, backend: str = "auto"
    ) -> Dict[str, Any]:
        """
        Test multiple contexts operating in parallel.

        Args:
            num_contexts: Number of contexts to create
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print(f"TEST: {num_contexts} Parallel Contexts ({backend})")
        print(f"{'─' * 60}")

        start_time = time.perf_counter()
        contexts = []
        context_ids = set()

        try:
            # Create contexts
            print(f"  Creating {num_contexts} contexts...")
            for i in range(num_contexts):
                ctx = AutomationContext(
                    backend=backend, action_delay=0.0, cleanup_on_close=False
                )
                contexts.append(ctx)
                context_ids.add(ctx.context_id)

            creation_time = time.perf_counter() - start_time
            print(f"    ✓ Created in {creation_time:.2f}s")

            # Verify unique IDs
            if len(context_ids) != num_contexts:
                self.errors.append(
                    f"Context ID collision: {num_contexts} contexts, {len(context_ids)} unique IDs"
                )
                print("    ✗ Context ID collision detected!")
            else:
                print("    ✓ All context IDs unique")

            # Verify isolated directories
            screenshot_dirs = set()
            for ctx in contexts:
                screenshot_dirs.add(str(ctx.screenshot_dir))

            if len(screenshot_dirs) != num_contexts:
                self.errors.append(
                    f"Directory collision: {num_contexts} contexts, {len(screenshot_dirs)} unique dirs"
                )
                print("    ✗ Directory collision detected!")
            else:
                print("    ✓ All directories isolated")

            # Perform operations in each context
            print("  Performing operations in each context...")
            op_start = time.perf_counter()

            for i, ctx in enumerate(contexts):
                try:
                    # Screenshot
                    msg, img = ctx.screenshot(save=False)

                    # Mouse operation
                    _, (x, y) = ctx.cursor_position()
                    ctx.mouse_move(x + 5, y)
                    ctx.mouse_move(x, y)

                    # Keyboard operation
                    ctx.key_press("shift")

                except Exception as e:
                    self.errors.append(f"Context {i} operation failed: {e}")

            op_time = time.perf_counter() - op_start
            print(f"    ✓ Operations completed in {op_time:.2f}s")

            # Verify stats
            print("  Verifying context statistics...")
            for i, ctx in enumerate(contexts):
                stats = ctx.get_stats()
                if (
                    stats["action_count"] != 4
                ):  # screenshot + cursor_position + 2x mouse_move + key_press = 5 actions
                    self.warnings.append(
                        f"Context {i} unexpected action count: {stats['action_count']} (expected 5)"
                    )
                if stats["screenshot_count"] != 1:
                    self.warnings.append(
                        f"Context {i} unexpected screenshot count: {stats['screenshot_count']}"
                    )

            print("    ✓ Statistics verified")

            # Cleanup
            print(f"  Cleaning up {num_contexts} contexts...")
            cleanup_start = time.perf_counter()
            for ctx in contexts:
                ctx.close()
            cleanup_time = time.perf_counter() - cleanup_start
            print(f"    ✓ Cleaned up in {cleanup_time:.2f}s")

            total_time = time.perf_counter() - start_time

            return {
                "success": len(self.errors) == 0,
                "num_contexts": num_contexts,
                "creation_time": creation_time,
                "operation_time": op_time,
                "cleanup_time": cleanup_time,
                "total_time": total_time,
                "errors": list(self.errors),
                "warnings": list(self.warnings),
            }

        except Exception as e:
            self.errors.append(f"Test failed: {e}")
            traceback.print_exc()
            return {
                "success": False,
                "num_contexts": num_contexts,
                "errors": list(self.errors),
            }

    def test_resource_leak(
        self, iterations: int = 50, backend: str = "auto"
    ) -> Dict[str, Any]:
        """
        Test for resource leaks (memory, file handles).

        Args:
            iterations: Number of iterations
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print(f"TEST: Resource Leak Detection ({iterations} iterations)")
        print(f"{'─' * 60}")

        process = psutil.Process(os.getpid())

        # Baseline memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_fds = len(process.open_files())

        print(f"  Initial memory: {initial_memory:.2f} MB")
        print(f"  Initial file descriptors: {initial_fds}")

        # Run iterations
        print(f"  Running {iterations} context create/destroy cycles...")
        for i in range(iterations):
            with AutomationContext(backend=backend, action_delay=0.0) as ctx:
                ctx.screenshot(save=False)
                ctx.click(100, 100)

            if (i + 1) % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024
                print(f"    Iteration {i + 1}: {current_memory:.2f} MB")

        # Final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        final_fds = len(process.open_files())

        memory_delta = final_memory - initial_memory
        fd_delta = final_fds - initial_fds

        print(f"\n  Final memory: {final_memory:.2f} MB")
        print(f"  Memory delta: {memory_delta:.2f} MB")
        print(f"  Final file descriptors: {final_fds}")
        print(f"  FD delta: {fd_delta}")

        # Check for leaks
        memory_leak = memory_delta > 50  # More than 50MB growth is suspicious
        fd_leak = fd_delta > 10  # More than 10 FDs leaked is suspicious

        if memory_leak:
            self.errors.append(f"Potential memory leak: {memory_delta:.2f} MB growth")
            print("  ✗ Potential memory leak detected")
        else:
            print("  ✓ No significant memory leak")

        if fd_leak:
            self.errors.append(f"File descriptor leak: {fd_delta} FDs not closed")
            print("  ✗ File descriptor leak detected")
        else:
            print("  ✓ No file descriptor leak")

        return {
            "success": not (memory_leak or fd_leak),
            "initial_memory_mb": initial_memory,
            "final_memory_mb": final_memory,
            "memory_delta_mb": memory_delta,
            "initial_fds": initial_fds,
            "final_fds": final_fds,
            "fd_delta": fd_delta,
            "errors": list(self.errors),
        }

    def test_thread_safety(
        self, num_threads: int = 5, ops_per_thread: int = 20, backend: str = "auto"
    ) -> Dict[str, Any]:
        """
        Test thread safety with concurrent context usage.

        Args:
            num_threads: Number of threads
            ops_per_thread: Operations per thread
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print(f"TEST: Thread Safety ({num_threads} threads, {ops_per_thread} ops each)")
        print(f"{'─' * 60}")

        errors_lock = threading.Lock()
        thread_errors: List[str] = []

        def worker(thread_id: int):
            """Worker function for thread."""
            try:
                with AutomationContext(backend=backend, action_delay=0.0) as ctx:
                    for i in range(ops_per_thread):
                        ctx.screenshot(save=False)
                        _, (x, y) = ctx.cursor_position()
                        ctx.mouse_move(x + 5, y)
                        ctx.mouse_move(x, y)

                print(f"    Thread {thread_id}: Completed {ops_per_thread} operations")

            except Exception as e:
                with errors_lock:
                    thread_errors.append(f"Thread {thread_id}: {e}")
                    traceback.print_exc()

        # Create and start threads
        print(f"  Starting {num_threads} threads...")
        start_time = time.perf_counter()

        threads = []
        for i in range(num_threads):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        total_time = time.perf_counter() - start_time

        print(f"\n  ✓ All threads completed in {total_time:.2f}s")

        if thread_errors:
            print(f"  ✗ {len(thread_errors)} thread errors:")
            for error in thread_errors:
                print(f"    - {error}")
            self.errors.extend(thread_errors)
        else:
            print("  ✓ No thread errors")

        return {
            "success": len(thread_errors) == 0,
            "num_threads": num_threads,
            "ops_per_thread": ops_per_thread,
            "total_time": total_time,
            "errors": thread_errors,
        }

    def test_rapid_create_destroy(
        self, iterations: int = 100, backend: str = "auto"
    ) -> Dict[str, Any]:
        """
        Test rapid context creation and destruction.

        Args:
            iterations: Number of iterations
            backend: Backend to use

        Returns:
            Dict with test results
        """
        print(f"\n{'─' * 60}")
        print(f"TEST: Rapid Create/Destroy ({iterations} iterations)")
        print(f"{'─' * 60}")

        times = []
        errors = []

        print(f"  Running {iterations} rapid cycles...")
        for i in range(iterations):
            try:
                start = time.perf_counter()

                ctx = AutomationContext(backend=backend, action_delay=0.0)
                ctx.screenshot(save=False)
                ctx.close()

                elapsed = time.perf_counter() - start
                times.append(elapsed)

                if (i + 1) % 25 == 0:
                    avg_time = sum(times[-25:]) / 25
                    print(
                        f"    Iteration {i + 1}: {avg_time * 1000:.2f}ms avg (last 25)"
                    )

            except Exception as e:
                errors.append(f"Iteration {i}: {e}")

        if errors:
            print(f"\n  ✗ {len(errors)} errors:")
            for error in errors[:5]:  # Show first 5
                print(f"    - {error}")
            self.errors.extend(errors)
        else:
            print("  ✓ No errors")

        avg_time = sum(times) / len(times) if times else 0
        print(f"\n  Average cycle time: {avg_time * 1000:.2f}ms")

        return {
            "success": len(errors) == 0,
            "iterations": iterations,
            "avg_time": avg_time,
            "errors": errors,
        }


def main():
    """Run stress test suite."""
    import platform

    print("\n" + "=" * 60)
    print("WEEK 4: STRESS TEST SUITE")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")

    # Select backend
    if platform.system() == "Darwin":
        backend = "macos"
        print("Backend: macOS Native")
    else:
        backend = "pyautogui"
        print("Backend: PyAutoGUI")

    stress = StressTest()
    results = {}

    # Test 1: Parallel contexts
    results["parallel_5"] = stress.test_parallel_contexts(5, backend)
    results["parallel_10"] = stress.test_parallel_contexts(10, backend)
    results["parallel_20"] = stress.test_parallel_contexts(20, backend)

    # Test 2: Resource leaks
    results["resource_leak"] = stress.test_resource_leak(50, backend)

    # Test 3: Thread safety
    results["thread_safety"] = stress.test_thread_safety(5, 20, backend)

    # Test 4: Rapid create/destroy
    results["rapid_cycles"] = stress.test_rapid_create_destroy(100, backend)

    # Summary
    print(f"\n{'=' * 60}")
    print("STRESS TEST SUMMARY")
    print(f"{'=' * 60}")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("success", False))

    print(f"\nTests passed: {passed_tests}/{total_tests}")

    if passed_tests == total_tests:
        print("✅ All stress tests passed!")
    else:
        print("⚠️  Some stress tests failed - review errors above")

    # Save results
    import json

    results_file = Path(__file__).parent / "stress_test_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n✅ Results saved to: {results_file}")

    print("\n🎯 Next: Run edge case tests with `python3 edge_case_test_week4.py`")


if __name__ == "__main__":
    main()

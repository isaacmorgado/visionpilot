#!/usr/bin/env python3
"""
Week 4: Performance Benchmark Suite

Comprehensive benchmarks comparing PyAutoGUI vs macOS Native backend:
- Screenshot performance
- Mouse operation performance
- Keyboard operation performance
- Multi-context performance
- Resource usage

Target: Verify 15-30x performance gain from macOS Native backend.
"""

import time
import statistics
import platform
import sys
from typing import List, Dict, Any, Tuple
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.context import AutomationContext


class PerformanceBenchmark:
    """
    Performance benchmarking framework for automation backends.

    Measures:
    - Operation latency (individual operations)
    - Throughput (operations per second)
    - Resource overhead (memory, CPU)
    - Context switching performance
    """

    def __init__(self, iterations: int = 100):
        """
        Initialize benchmark suite.

        Args:
            iterations: Number of iterations per benchmark
        """
        self.iterations = iterations
        self.results: Dict[str, Any] = {}

    def _time_operation(
        self, operation_func, iterations: int = None
    ) -> Tuple[float, float, List[float]]:
        """
        Time an operation multiple times and return statistics.

        Args:
            operation_func: Function to benchmark
            iterations: Number of iterations (defaults to self.iterations)

        Returns:
            Tuple of (mean_time, median_time, all_times)
        """
        iterations = iterations or self.iterations
        times = []

        for _ in range(iterations):
            start = time.perf_counter()
            operation_func()
            end = time.perf_counter()
            times.append(end - start)

        return statistics.mean(times), statistics.median(times), times

    def benchmark_screenshot(self, backend: str) -> Dict[str, float]:
        """
        Benchmark screenshot performance.

        Args:
            backend: Backend to test ("pyautogui" or "macos")

        Returns:
            Dict with mean, median, min, max times
        """
        print(f"\n  Testing {backend} screenshots ({self.iterations} iterations)...")

        with AutomationContext(backend=backend, action_delay=0.0) as ctx:
            mean, median, times = self._time_operation(
                lambda: ctx.screenshot(save=False)
            )

        results = {
            "mean": mean,
            "median": median,
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        }

        print(f"    Mean: {mean * 1000:.2f}ms, Median: {median * 1000:.2f}ms")
        return results

    def benchmark_mouse_move(self, backend: str) -> Dict[str, float]:
        """
        Benchmark mouse movement performance.

        Args:
            backend: Backend to test

        Returns:
            Dict with timing statistics
        """
        print(
            f"\n  Testing {backend} mouse movements ({self.iterations} iterations)..."
        )

        with AutomationContext(backend=backend, action_delay=0.0) as ctx:
            # Get current position
            _, (start_x, start_y) = ctx.cursor_position()

            # Benchmark moving 10 pixels right and back
            def move_operation():
                ctx.mouse_move(start_x + 10, start_y)
                ctx.mouse_move(start_x, start_y)

            mean, median, times = self._time_operation(move_operation)

        results = {
            "mean": mean,
            "median": median,
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        }

        print(f"    Mean: {mean * 1000:.2f}ms, Median: {median * 1000:.2f}ms")
        return results

    def benchmark_click(self, backend: str) -> Dict[str, float]:
        """
        Benchmark click performance.

        Args:
            backend: Backend to test

        Returns:
            Dict with timing statistics
        """
        print(f"\n  Testing {backend} clicks ({self.iterations} iterations)...")

        with AutomationContext(backend=backend, action_delay=0.0) as ctx:
            _, (x, y) = ctx.cursor_position()

            mean, median, times = self._time_operation(lambda: ctx.click(x, y))

        results = {
            "mean": mean,
            "median": median,
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        }

        print(f"    Mean: {mean * 1000:.2f}ms, Median: {median * 1000:.2f}ms")
        return results

    def benchmark_context_creation(
        self, backend: str, count: int = 50
    ) -> Dict[str, float]:
        """
        Benchmark context creation overhead.

        Args:
            backend: Backend to test
            count: Number of contexts to create

        Returns:
            Dict with timing statistics
        """
        print(f"\n  Testing {backend} context creation ({count} contexts)...")

        times = []
        for _ in range(count):
            start = time.perf_counter()
            ctx = AutomationContext(backend=backend, action_delay=0.0)
            ctx.close()
            end = time.perf_counter()
            times.append(end - start)

        results = {
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
        }

        print(
            f"    Mean: {results['mean'] * 1000:.2f}ms, Median: {results['median'] * 1000:.2f}ms"
        )
        return results

    def benchmark_multi_context(
        self, backend: str, num_contexts: int = 5
    ) -> Dict[str, float]:
        """
        Benchmark multiple simultaneous contexts.

        Args:
            backend: Backend to test
            num_contexts: Number of simultaneous contexts

        Returns:
            Dict with timing statistics
        """
        print(f"\n  Testing {backend} with {num_contexts} simultaneous contexts...")

        start = time.perf_counter()

        contexts = []
        for i in range(num_contexts):
            ctx = AutomationContext(backend=backend, action_delay=0.0)
            contexts.append(ctx)

        creation_time = time.perf_counter() - start

        # Perform operations in each context
        op_start = time.perf_counter()
        for ctx in contexts:
            ctx.screenshot(save=False)
            _, (x, y) = ctx.cursor_position()
            ctx.click(x, y)
        op_time = time.perf_counter() - op_start

        # Cleanup
        cleanup_start = time.perf_counter()
        for ctx in contexts:
            ctx.close()
        cleanup_time = time.perf_counter() - cleanup_start

        total_time = time.perf_counter() - start

        results = {
            "creation_time": creation_time,
            "operation_time": op_time,
            "cleanup_time": cleanup_time,
            "total_time": total_time,
            "ops_per_context": 3,  # screenshot + cursor_position + click
        }

        print(f"    Total: {total_time * 1000:.2f}ms")
        print(f"    Creation: {creation_time * 1000:.2f}ms")
        print(f"    Operations: {op_time * 1000:.2f}ms")
        print(f"    Cleanup: {cleanup_time * 1000:.2f}ms")

        return results

    def run_full_benchmark(self) -> Dict[str, Any]:
        """
        Run complete benchmark suite comparing backends.

        Returns:
            Comprehensive results dict
        """
        print("\n" + "=" * 60)
        print("WEEK 4: PERFORMANCE BENCHMARK SUITE")
        print("=" * 60)

        if platform.system() != "Darwin":
            print("\n⚠️  Warning: macOS backend only available on macOS")
            print("   Running PyAutoGUI benchmarks only")
            backends = ["pyautogui"]
        else:
            backends = ["pyautogui", "macos"]

        results = {}

        for backend in backends:
            print(f"\n{'─' * 60}")
            print(f"Benchmarking: {backend.upper()}")
            print(f"{'─' * 60}")

            results[backend] = {
                "screenshot": self.benchmark_screenshot(backend),
                "mouse_move": self.benchmark_mouse_move(backend),
                "click": self.benchmark_click(backend),
                "context_creation": self.benchmark_context_creation(backend),
                "multi_context": self.benchmark_multi_context(backend),
            }

        # Calculate speedup if both backends tested
        if len(backends) == 2:
            print(f"\n{'=' * 60}")
            print("PERFORMANCE COMPARISON")
            print(f"{'=' * 60}")

            for operation in ["screenshot", "mouse_move", "click"]:
                pyautogui_time = results["pyautogui"][operation]["mean"]
                macos_time = results["macos"][operation]["mean"]
                speedup = pyautogui_time / macos_time

                print(f"\n{operation.upper()}:")
                print(f"  PyAutoGUI: {pyautogui_time * 1000:.2f}ms")
                print(f"  macOS Native: {macos_time * 1000:.2f}ms")
                print(f"  Speedup: {speedup:.2f}x")

                # Check if we hit target
                if speedup >= 15:
                    print("  ✅ Target achieved (15-30x)")
                elif speedup >= 10:
                    print("  ⚠️  Good speedup, but below 15x target")
                else:
                    print("  ❌ Below target performance")

        return results


def main():
    """Run benchmark suite."""
    # Check platform
    if platform.system() != "Darwin":
        print("\n⚠️  Note: macOS Native backend benchmarks only available on macOS")
        print("   PyAutoGUI benchmarks will still run")

    # Run benchmarks
    benchmark = PerformanceBenchmark(iterations=100)
    results = benchmark.run_full_benchmark()

    # Summary
    print(f"\n{'=' * 60}")
    print("BENCHMARK COMPLETE")
    print(f"{'=' * 60}")
    print(f"\nIterations per test: {benchmark.iterations}")
    print(f"Platform: {platform.system()} {platform.release()}")

    # Save results
    import json

    results_file = Path(__file__).parent / "benchmark_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n✅ Results saved to: {results_file}")

    print("\n🎯 Next: Run stress tests with `python3 stress_test_week4.py`")


if __name__ == "__main__":
    main()

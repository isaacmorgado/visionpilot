#!/usr/bin/env python3
"""
Week 4: Master Test Runner

Runs all Week 4 test suites in sequence:
1. Performance benchmarks
2. Stress tests
3. Edge case tests

Generates a consolidated report.
"""

import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, Any


def run_test_script(script_name: str, description: str) -> Dict[str, Any]:
    """
    Run a test script and capture results.

    Args:
        script_name: Name of the test script
        description: Human-readable description

    Returns:
        Dict with test results
    """
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
        }

    print(f"\n{'=' * 60}")
    print(f"Running: {description}")
    print(f"Script: {script_name}")
    print(f"{'=' * 60}\n")

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        elapsed_time = time.time() - start_time

        # Print output
        print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "elapsed_time": elapsed_time,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "error": "Test timeout (10 minutes exceeded)",
            "elapsed_time": elapsed_time,
        }

    except Exception as e:
        elapsed_time = time.time() - start_time
        return {
            "success": False,
            "error": str(e),
            "elapsed_time": elapsed_time,
        }


def main():
    """Run all Week 4 test suites."""
    import platform

    print("\n" + "=" * 80)
    print(" " * 20 + "WEEK 4: MASTER TEST RUNNER")
    print("=" * 80)
    print(f"\nPlatform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Working directory: {Path(__file__).parent}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Define test suites
    test_suites = [
        ("benchmark_week4.py", "Performance Benchmarks"),
        ("stress_test_week4.py", "Stress Tests"),
        ("edge_case_test_week4.py", "Edge Case Tests"),
    ]

    # Run all tests
    results = {}
    total_start_time = time.time()

    for script_name, description in test_suites:
        results[script_name] = run_test_script(script_name, description)

        # Brief pause between tests
        time.sleep(1)

    total_elapsed_time = time.time() - total_start_time

    # Generate consolidated report
    print("\n" + "=" * 80)
    print(" " * 20 + "CONSOLIDATED WEEK 4 TEST REPORT")
    print("=" * 80)

    # Summary table
    print(f"\n{'Test Suite':<40} {'Status':<10} {'Time':<10}")
    print("-" * 60)

    all_passed = True
    for script_name, description in test_suites:
        result = results[script_name]
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        elapsed = f"{result['elapsed_time']:.2f}s"

        print(f"{description:<40} {status:<10} {elapsed:<10}")

        if not result["success"]:
            all_passed = False
            if "error" in result:
                print(f"  Error: {result['error']}")

    print("-" * 60)
    print(f"{'Total':<40} {'':<10} {total_elapsed_time:.2f}s")

    # Check for result files
    print("\n\nGenerated Result Files:")
    result_files = [
        "benchmark_results.json",
        "stress_test_results.json",
        "edge_case_results.json",
    ]

    for filename in result_files:
        file_path = Path(__file__).parent / filename
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✓ {filename} ({size} bytes)")
        else:
            print(f"  ✗ {filename} (not found)")

    # Final verdict
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL WEEK 4 TESTS PASSED 🎉")
        print("\nWeek 4 implementation is complete and verified:")
        print("  ✅ Performance benchmarks completed")
        print("  ✅ Stress tests passed")
        print("  ✅ Edge cases handled")
        print("\n🎯 Next: Week 5 - Documentation and migration guide")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nReview the output above for details.")
        print("Fix any issues before proceeding to Week 5.")

    print("=" * 80)

    # Save consolidated report
    import json

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "platform": platform.system(),
        "python_version": sys.version.split()[0],
        "total_elapsed_time": total_elapsed_time,
        "all_passed": all_passed,
        "test_suites": {
            description: {
                "script": script_name,
                "success": results[script_name]["success"],
                "elapsed_time": results[script_name]["elapsed_time"],
            }
            for script_name, description in test_suites
        },
    }

    report_file = Path(__file__).parent / "week4_master_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✅ Consolidated report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()

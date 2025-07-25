#!/usr/bin/env python3
"""
Test runner script for the FastAPI application test suite.
"""
import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run FastAPI application tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument(
        "--integration", action="store_true", help="Run integration tests only"
    )
    parser.add_argument("--api", action="store_true", help="Run API tests only")
    parser.add_argument(
        "--coverage", action="store_true", help="Run with coverage report"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--parallel", "-n", type=int, help="Number of parallel workers")
    parser.add_argument("--file", "-f", help="Run specific test file")
    parser.add_argument("--marker", "-m", help="Run tests with specific marker")

    args = parser.parse_args()

    # Base pytest command
    cmd = ["pytest"]

    # Add verbosity
    if args.verbose:
        cmd.append("-v")

    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])

    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=html", "--cov-report=term-missing"])

    # Add marker
    if args.marker:
        cmd.extend(["-m", args.marker])

    # Determine what to run
    if args.file:
        cmd.append(args.file)
    elif args.unit:
        cmd.append("tests/unit/")
    elif args.integration:
        cmd.append("tests/integration/")
    elif args.api:
        cmd.append("tests/api/")
    else:
        # Run all tests
        cmd.append("tests/")

    # Run the tests
    success = run_command(cmd, "Test execution")

    if success:
        print("\n🎉 All tests completed successfully!")
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - Terminal: See output above")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()

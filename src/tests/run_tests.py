#!/usr/bin/env python
"""
Test runner script for wallet project.

This script provides convenient commands to run different types of tests.
"""
import argparse
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}\n")

    try:
        subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} failed with exit code {e.returncode}")
        return False


def run_unit_tests():
    """Run unit tests."""
    cmd = ["python", "-m", "pytest", "src/tests/unit/", "-v", "--tb=short"]
    return run_command(cmd, "Unit Tests")


def run_functional_tests():
    """Run functional tests."""
    cmd = ["python", "-m", "pytest", "src/tests/functional/", "-v", "--tb=short"]
    return run_command(cmd, "Functional Tests")


def run_integration_tests():
    """Run integration tests."""
    cmd = ["python", "-m", "pytest", "src/tests/integration/", "-v", "--tb=short"]
    return run_command(cmd, "Integration Tests")


def run_all_tests():
    """Run all tests."""
    cmd = [
        "python",
        "-m",
        "pytest",
        "src/tests/",
        "-v",
        "--tb=short",
        "--cov=wallets",
        "--cov-report=term-missing",
        "--cov-report=html",
    ]
    return run_command(cmd, "All Tests with Coverage")


def run_linting():
    """Run code linting."""
    cmd = ["ruff", "check", "src/"]
    return run_command(cmd, "Code Linting (Ruff)")


def run_formatting():
    """Run code formatting."""
    cmd = ["black", "src/"]
    return run_command(cmd, "Code Formatting (Black)")


def run_type_checking():
    """Run type checking."""
    cmd = ["mypy", "src/"]
    return run_command(cmd, "Type Checking (MyPy)")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test runner for wallet project")
    parser.add_argument(
        "test_type",
        choices=[
            "unit",
            "functional",
            "integration",
            "all",
            "lint",
            "format",
            "type-check",
            "full",
        ],
        help="Type of tests to run",
    )

    args = parser.parse_args()

    success = True

    if args.test_type == "unit":
        success = run_unit_tests()
    elif args.test_type == "functional":
        success = run_functional_tests()
    elif args.test_type == "integration":
        success = run_integration_tests()
    elif args.test_type == "all":
        success = run_all_tests()
    elif args.test_type == "lint":
        success = run_linting()
    elif args.test_type == "format":
        success = run_formatting()
    elif args.test_type == "type-check":
        success = run_type_checking()
    elif args.test_type == "full":
        # Run all checks
        success = (
            run_linting()
            and run_formatting()
            and run_type_checking()
            and run_all_tests()
        )

    if success:
        print("\n🎉 All operations completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Some operations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()

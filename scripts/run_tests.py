#!/usr/bin/env python3
"""
Test runner for the current Phantom package layout.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_command(cmd: list[str], description: str) -> bool:
    print(f"\n[run] {description}")
    print(" ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phantom tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--safe", action="store_true", help="Run the safe unit test subset")
    parser.add_argument("--coverage", action="store_true", help="Enable pytest coverage output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose pytest output")
    args = parser.parse_args()

    cmd = [sys.executable, "-m", "pytest"]
    if args.verbose:
        cmd.append("-v")
    if args.coverage:
        cmd.extend(["--cov=phantom", "--cov-report=term-missing"])

    if args.all:
        cmd.append("tests")
        description = "all tests"
    else:
        cmd.append("tests/test_config_database.py")
        description = "safe unit tests"

    return 0 if run_command(cmd, description) else 1


if __name__ == "__main__":
    raise SystemExit(main())

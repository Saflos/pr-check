"""The tiny bit of code your gate has to protect.

There is a real bug in here. It passes on Linux and fails on Windows.
Do not fix it yet. Build the gate first, let the gate catch it, then fix it.
"""
import os
import sys

REPORT = os.path.join("data","reports","summary.txt")


def report_path() -> str:
    """Where the nightly report gets written."""
    return os.path.join("data", "reports", "summary.txt")


def main() -> int:
    if report_path() != REPORT:
        print(f"Path mismatch: {report_path()!r} is not {REPORT!r}")
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())

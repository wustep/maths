#!/usr/bin/env python3
"""Run the finite certificates. Exit nonzero on a failed check."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(script: str, extra: list[str] | None = None) -> int:
    cmd = [sys.executable, str(ROOT / script)] + (extra or [])
    print("+", " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def main() -> int:
    rc = 0
    rc |= run("trivial_cover.py")
    rc |= run("obstruction.py")
    rc |= run("g_of_y.py", ["--y-max", "61"])
    rc |= run("covering_search.py")
    print("ALL_OK" if rc == 0 else "FAILED", flush=True)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

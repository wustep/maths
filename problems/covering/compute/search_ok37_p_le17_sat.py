#!/usr/bin/env python3
"""Compatibility entry point; the OK37 campaign lives in q12."""
import runpy
from pathlib import Path

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).resolve().parent / "q12" /
                       "search_ok37_p_le17_sat.py"), run_name="__main__")

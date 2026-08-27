#!/usr/bin/env python3
"""Re-export the q1 sequential-counter encoder.

Load q1/encode.py by path so this wrapper is never registered as the
``encode`` module (that circular-imports when q4 is on sys.path).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

Q1 = Path(__file__).resolve().parent.parent / "q1"
_spec = importlib.util.spec_from_file_location("_q1_encode", Q1 / "encode.py")
_q1 = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_q1)

encode = _q1.encode
main = _q1.main
sinz_atleast = _q1.sinz_atleast
sinz_atmost = _q1.sinz_atmost
sinz_exactly = _q1.sinz_exactly
var_id = _q1.var_id
write_cnf = _q1.write_cnf

__all__ = [
    "encode",
    "main",
    "sinz_atleast",
    "sinz_atmost",
    "sinz_exactly",
    "var_id",
    "write_cnf",
]


if __name__ == "__main__":
    main()

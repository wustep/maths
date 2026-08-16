"""Import-check the Python sidecar. Not a mathematical result."""

from __future__ import annotations

REQUIRED = [
    "sympy",
    "numpy",
    "scipy",
    "mpmath",
    "pandas",
    "matplotlib",
    "networkx",
    "pulp",
    "ortools",
    "galois",
    "flint",
    "cvxpy",
    "gmpy2",
    "z3",
    "IPython",
    "pytest",
]


def check_imports() -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for name in REQUIRED:
        try:
            mod = __import__(name)
            rows.append((name, getattr(mod, "__version__", "ok")))
        except Exception as exc:  # noqa: BLE001 — report any import failure
            rows.append((name, f"FAIL: {exc}"))
    return rows


def main() -> int:
    bad = 0
    for name, status in check_imports():
        print(f"{name:12} {status}")
        if status.startswith("FAIL"):
            bad += 1
    return bad

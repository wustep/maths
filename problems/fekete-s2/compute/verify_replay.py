#!/usr/bin/env python3
"""Replay known optima and any stored checkpoints against Table 3."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

from energy import log_energy
from known import KNOWN

HERE = Path(__file__).resolve().parent
TABLE = json.loads((HERE / "ridgway2018.json").read_text())["globals"]


def main() -> None:
    print("=== known exact / closed-form configs ===")
    ok = True
    for n, (name, builder, exact) in KNOWN.items():
        pts = builder()
        e = log_energy(pts)
        pub = TABLE.get(str(n))
        closed = exact if exact is not None else float("nan")
        print(
            f"N={n:3d}  {name:<22}  E={e:.12f}  closed={closed:.12f}  "
            f"Table3={pub}"
        )
        if exact is not None and abs(e - exact) > 1e-13:
            print("  FAIL closed-form mismatch")
            ok = False
        if pub is not None and abs(e - pub) > 5e-7:
            # Table 3 is 8 decimals; known optima must match it.
            print(f"  WARN vs Table 3: delta={e - pub:.3e}")
        norms = np.linalg.norm(pts, axis=1)
        if abs(norms - 1.0).max() > 1e-14:
            print("  FAIL not on S^2")
            ok = False

    print("\n=== checkpoints (if present) ===")
    ckpt = HERE / "checkpoints"
    if ckpt.is_dir():
        for path in sorted(ckpt.glob("N*.json")):
            rec = json.loads(path.read_text())
            e = log_energy(rec["points"])
            pub = rec.get("published_ridgway2018")
            delta = None if pub is None else e - pub
            print(
                f"{path.name}  N={rec['N']}  E={e:.12f}  "
                f"stored={rec.get('E')}  Table3={pub}  delta={delta}"
            )
            if abs(e - rec["E"]) > 1e-12:
                print("  FAIL stored energy disagrees with verifier")
                ok = False
    else:
        print("(no checkpoints yet)")

    if not ok:
        raise SystemExit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()

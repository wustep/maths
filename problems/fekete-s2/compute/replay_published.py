#!/usr/bin/env python3
"""Replay Rathbun–Ridgway (arXiv:2008.04880 / Zenodo 5595366) coordinates.

Parses GP-Pari files `log.3.N.80` from a local directory (default
/tmp/fekete-data/rathbun). Recomputes E with energy.py and compares to
the file's printed ener= and to Ridgway–Cheviakov Table 3.
Does not download; fetch the zip yourself if the cache is missing.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

from energy import log_energy

HERE = Path(__file__).resolve().parent
TABLE = json.loads((HERE / "ridgway2018.json").read_text())["globals"]


def parse_pari(path: Path):
    text = path.read_text()
    # p=[[x,y,z], ...];
    m = re.search(r"p\s*=\s*(\[.*?\])\s*;", text, re.S)
    if not m:
        raise ValueError(f"no p=[...] in {path}")
    raw = m.group(1)
    # drop whitespace, then json-ish
    raw = raw.replace("\n", "")
    # Some algebraic files write 1/2 instead of 0.5.
    raw = re.sub(r"(?<![\d.])(-?\d+)/(\d+)(?![\d.])", lambda m: str(float(m.group(1)) / float(m.group(2))), raw)
    pts = json.loads(raw)
    ener = None
    em = re.search(r"ener\s*=\s*([+-]?\d+\.\d+)", text)
    if em:
        ener = float(em.group(1))
    return np.asarray(pts, dtype=np.float64), ener


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", type=Path, default=Path("/tmp/fekete-data/rathbun"))
    ap.add_argument("--out", type=Path, default=HERE / "replay_rathbun.json")
    args = ap.parse_args()
    if not args.dir.is_dir():
        raise SystemExit(
            f"missing {args.dir}. Unzip Zenodo 5595366 log.0-65.zip there."
        )

    rows = []
    print(f"{'N':>3}  {'E_ours':>16}  {'ener_file':>16}  {'Table3':>14}  {'d_file':>10}  {'d_T3':>10}")
    for n in range(2, 66):
        path = args.dir / f"log.3.{n}.80"
        if not path.exists():
            print(f"N={n} missing {path.name}")
            continue
        pts, ener = parse_pari(path)
        e = log_energy(pts)
        pub = TABLE.get(str(n))
        d_file = None if ener is None else e - ener
        d_t3 = None if pub is None else e - pub
        rows.append(
            {
                "N": n,
                "E": e,
                "ener_file": ener,
                "table3": pub,
                "delta_file": d_file,
                "delta_table3": d_t3,
            }
        )
        print(
            f"{n:3d}  {e:16.10f}  {ener if ener is not None else float('nan'):16.10f}  "
            f"{pub if pub is not None else float('nan'):14.8f}  "
            f"{d_file if d_file is not None else float('nan'):10.2e}  "
            f"{d_t3 if d_t3 is not None else float('nan'):10.2e}"
        )

    payload = {
        "_source": "Rathbun–Ridgway arXiv:2008.04880, Zenodo 10.5281/zenodo.5595366, files log.3.N.80",
        "_verifier": "energy.py, float64 after project-to-S^2",
        "rows": rows,
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()

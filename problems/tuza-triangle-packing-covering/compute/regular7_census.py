#!/usr/bin/env python3
"""(nu, tau) for small 7-regular graphs. Gupta Question 12.3."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tuza import nu_tau_ilp
from wke import parse_g6

HERE = Path(__file__).resolve().parent
GENG = Path(__file__).resolve().parent / "bin" / "geng"
OUT = HERE / "certs"
OUT.mkdir(exist_ok=True)


def geng_reg(n, d):
    proc = subprocess.run(
        [str(GENG), "-q", f"-d{d}", f"-D{d}", str(n)],
        capture_output=True,
        text=True,
        check=True,
    )
    for line in proc.stdout.splitlines():
        parsed = parse_g6(line)
        if parsed:
            yield parsed[0], parsed[1], line.strip()


def main():
    ns = [int(x) for x in sys.argv[1:]] or [8, 10, 12]
    all_out = {}
    for n in ns:
        print(f"=== {7}-regular n={n} ===", flush=True)
        recs = []
        n_tight = 0
        n_cex = 0
        max_ratio = 0.0
        max_ex = None
        count = 0
        for nv, edges, g6 in geng_reg(n, 7):
            count += 1
            nu, tau = nu_tau_ilp(edges, list(range(nv)))
            ratio = None if nu == 0 else tau / nu
            rec = {"g6": g6, "nu": nu, "tau": tau, "ratio": ratio, "n_edges": len(edges)}
            recs.append(rec)
            if nu and tau > 2 * nu:
                n_cex += 1
                print(f"COUNTEREXAMPLE {g6} {rec}", flush=True)
            if nu and tau == 2 * nu:
                n_tight += 1
                print(f"TIGHT 7-regular {g6} {rec}", flush=True)
            if ratio is not None and ratio > max_ratio:
                max_ratio = ratio
                max_ex = rec
            if count % 20 == 0:
                print(f"  progress {count} max_ratio={max_ratio}", flush=True)
        summary = {
            "n": n,
            "graphs": count,
            "tight": n_tight,
            "cex": n_cex,
            "max_ratio": max_ratio,
            "max_ex": max_ex,
            "records": recs,
        }
        all_out[str(n)] = summary
        print(
            f"n={n} graphs={count} tight={n_tight} max_ratio={max_ratio} ex={max_ex}",
            flush=True,
        )
    (OUT / "regular7_census.json").write_text(json.dumps(all_out, indent=2) + "\n")


if __name__ == "__main__":
    main()

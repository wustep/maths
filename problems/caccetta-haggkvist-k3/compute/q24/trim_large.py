#!/usr/bin/env python3
"""Trim keep/*.drat files above a size cutoff, optionally capped by n."""

from __future__ import annotations

import argparse
from pathlib import Path

from trim_keep import KEEP, parse_stem, trim_keep_file


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-mb", type=float, default=8.0)
    ap.add_argument("--n-min", type=int, default=0)
    ap.add_argument("--n-max", type=int, default=10**9)
    args = ap.parse_args()
    min_bytes = int(args.min_mb * 1024 * 1024)
    rows = []
    for path in sorted(KEEP.glob("ch-*-*-k*.drat")):
        parsed = parse_stem(path)
        if parsed is None:
            continue
        n, d, k = parsed
        if n < args.n_min or n > args.n_max or path.stat().st_size < min_bytes:
            continue
        print(f"TRIM n={n} d={d} k={k} raw={path.stat().st_size}", flush=True)
        rec = trim_keep_file(n, d, k, min_bytes=min_bytes)
        print(
            f"  ok={rec.get('ok')} replaced={rec.get('replaced')} "
            f"core={rec.get('core_bytes')} err={rec.get('error')}",
            flush=True,
        )
        rows.append(rec)
    bad = sum(1 for r in rows if not r.get("ok"))
    print("DONE", len(rows), "failures", bad)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()

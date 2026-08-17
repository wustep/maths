#!/usr/bin/env python3
"""Try to add one vertex to every circulant (5,5,n)-graph we dumped."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from r55lib import circulant_nbr, dump_json, is_ramsey

ROOT = Path(__file__).resolve().parent
EXT = ROOT / "extend_one"


def parse_hits(path: Path) -> list[tuple[int, list[int]]]:
    out = []
    for line in path.read_text().splitlines():
        if not line.startswith("HIT "):
            continue
        # HIT n=41 deg=20 S=1 2 3 ... mask=...
        body = line.split("S=", 1)[1]
        s_part = body.split("mask=")[0].strip()
        S = [int(x) for x in s_part.split() if x]
        n = int(line.split("n=")[1].split()[0])
        out.append((n, S))
    return out


def extend_graph(nbr: list[int]) -> dict:
    n = len(nbr)
    payload = f"{n}\n" + "\n".join(str(x) for x in nbr) + "\n"
    r = subprocess.run([str(EXT)], input=payload, text=True, capture_output=True)
    exts = []
    summary = r.stdout.strip().splitlines()
    head = summary[0] if summary else ""
    for line in summary[1:]:
        if line.startswith("EXT "):
            # EXT i 0xMASK pop=k
            parts = line.split()
            mask = int(parts[2], 16)
            pop = int(parts[3].split("=")[1])
            exts.append({"mask": mask, "deg": pop})
    return {"head": head, "n_ext": len(exts), "exts": exts, "stderr": r.stderr}


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: extend_circulants.py dump.txt")
        return 2
    path = Path(sys.argv[1])
    hits = parse_hits(path)
    t0 = time.time()
    recs = []
    any_ext = 0
    for i, (n, S) in enumerate(hits):
        nbr = circulant_nbr(n, S)
        assert is_ramsey(nbr), (n, S)
        info = extend_graph(nbr)
        info["i"] = i
        info["n"] = n
        info["S"] = S
        recs.append(info)
        any_ext += info["n_ext"]
        print(f"{i}/{len(hits)} n={n} S={S} ext={info['n_ext']} {info['head']}", flush=True)
    out = {
        "source": str(path),
        "n_seeds": len(hits),
        "n_extensions_total": any_ext,
        "seconds": round(time.time() - t0, 3),
        "records": recs,
    }
    dest = ROOT / "certs" / f"extend_{path.stem}.json"
    dump_json(str(dest), out)
    print("wrote", dest, "total_ext", any_ext)
    return 0


if __name__ == "__main__":
    sys.exit(main())

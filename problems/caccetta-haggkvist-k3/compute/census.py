#!/usr/bin/env python3
"""Exact CH-triangle SAT census for small n.

For each n, let d★ = ⌈n/3⌉ (the conjectured forcing degree) and
d_cyc = ⌊(n−1)/3⌋ (the cyclic construction).  SAT on a d-outregular
C3-free oriented graph.  Encoding: encode_ch.py (binomial cardinality,
N⁺(0) fixed, lex SB off for the numbers below — they were checked
with the verifier).

Kissat 4.0.4.  A SAT model is replayed by verify_model.py.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
KISSAT = HERE / "kissat"
OUT = HERE / "certs"


def run(n, d, secs=30, sb=False):
    extra = [] if sb else ["--no-sb"]
    cnf = Path(f"/tmp/census-{n}-{d}{'-sb' if sb else ''}.cnf")
    out = Path(f"/tmp/census-{n}-{d}.out")
    subprocess.check_call(
        ["python3", str(HERE / "encode_ch.py"), "--n", str(n), "--d", str(d), *extra],
        stdout=open(cnf, "w"),
    )
    header = cnf.read_text().splitlines()[0]
    with open(out, "w") as f:
        subprocess.call([str(KISSAT), "-q", f"--time={secs}", str(cnf)], stdout=f, stderr=subprocess.STDOUT)
    text = out.read_text()
    ver = subprocess.check_output(
        ["python3", str(HERE / "verify_model.py"), str(n), str(d)],
        input=text,
        text=True,
    ).strip()
    if ver == "UNSAT":
        status = "UNSAT"
        ok = True
        model = None
    elif ver.startswith("{"):
        info = ast.literal_eval(ver)
        status = "SAT"
        ok = bool(info.get("ok"))
        model = info
    else:
        status = "UNKNOWN"
        ok = False
        model = ver
    return {"n": n, "d": d, "header": header, "status": status, "verified": ok, "model": model}


def main():
    rows = []
    # Construction / conjecture pairs, plus a few off-diagonal checks.
    jobs = []
    for n in range(4, 12):
        dstar = (n + 2) // 3
        dcyc = (n - 1) // 3
        jobs.append((n, dcyc, 20))
        if dstar != dcyc:
            jobs.append((n, dstar, 20))
    # known theorems / first open
    jobs += [(12, 4, 60), (12, 3, 20)]
    seen = set()
    for n, d, t in jobs:
        if (n, d) in seen or d <= 0:
            continue
        seen.add((n, d))
        print(f"solve n={n} d={d} ...", flush=True)
        rec = run(n, d, secs=t)
        print(f"  {rec['status']} verified={rec['verified']} {rec['header']}", flush=True)
        # drop huge arc lists from the saved census
        if rec["model"] and isinstance(rec["model"], dict):
            rec["model"] = {k: rec["model"][k] for k in rec["model"] if k != "arcs"}
        rows.append(rec)
    path = OUT / "small_n_census.json"
    path.write_text(json.dumps(rows, indent=2))
    print("wrote", path)


if __name__ == "__main__":
    main()

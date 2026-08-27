#!/usr/bin/env python3
"""Encode one (n,d[,k]) cube, run kissat, optionally check a DRAT proof."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

Q1 = Path(__file__).resolve().parent.parent / "q1"
sys.path.insert(0, str(Q1))

from encode import encode, write_cnf
from verify_model import check, parse_model

HERE = Path(__file__).resolve().parent
BIN = HERE / "bin"
CERTS = HERE / "certs"


def find_bin(name: str) -> Path:
    env = os.environ.get(name.upper())
    if env and Path(env).exists():
        return Path(env)
    for p in (BIN / name, HERE / name, Path("/tmp/solvers") / name):
        if p.is_file():
            return p
    kissat = Path("/tmp/solvers/kissat/build/kissat")
    if name == "kissat" and kissat.exists():
        return kissat
    found = subprocess.run(["which", name], capture_output=True, text=True)
    if found.returncode == 0:
        return Path(found.stdout.strip())
    raise FileNotFoundError(name)


def run_one(
    n: int,
    d: int,
    secs: int,
    indeg0: int | None,
    exact_in: bool,
    sb: bool,
    proof: bool,
    tag: str | None,
    u_from_1: int | None = None,
    nplus1_from_2: int | None = None,
    extra_args: list[str] | None = None,
) -> dict:
    CERTS.mkdir(exist_ok=True)
    suffix = []
    if indeg0 is not None:
        suffix.append(f"k{indeg0}")
    if u_from_1 is not None:
        suffix.append(f"t{u_from_1}")
    if nplus1_from_2 is not None:
        suffix.append(f"s{nplus1_from_2}")
    if exact_in:
        suffix.append("ein")
    if not sb:
        suffix.append("nosb")
    stem = tag or f"ch-{n}-{d}" + (("-" + "-".join(suffix)) if suffix else "")
    cnf_path = CERTS / f"{stem}.cnf"
    out_path = CERTS / f"{stem}.out"
    proof_path = CERTS / f"{stem}.drat"

    clauses, nvars = encode(
        n,
        d,
        exact=True,
        sb=sb,
        indeg0=indeg0,
        exact_in=exact_in,
        u_from_1=u_from_1,
        nplus1_from_2=nplus1_from_2,
    )
    with cnf_path.open("w") as f:
        write_cnf(clauses, nvars, f)
    header = f"p cnf {nvars} {len(clauses)}"

    kissat = find_bin("kissat")
    cmd = [str(kissat), f"--time={secs}", str(cnf_path)]
    if extra_args:
        cmd[1:1] = extra_args
    if proof:
        cmd.append(str(proof_path))
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    text = proc.stdout + proc.stderr
    out_path.write_text(text)

    status = "UNKNOWN"
    if "s UNSATISFIABLE" in text:
        status = "UNSAT"
    elif "s SATISFIABLE" in text:
        status = "SAT"

    rec = {
        "n": n,
        "d": d,
        "indeg0": indeg0,
        "u_from_1": u_from_1,
        "nplus1_from_2": nplus1_from_2,
        "exact_in": exact_in,
        "sb": sb,
        "header": header,
        "status": status,
        "time_s": round(dt, 3),
        "timeout_s": secs,
        "returncode": proc.returncode,
        "cnf": str(cnf_path.name),
        "out": str(out_path.name),
    }
    conflicts = None
    for line in text.splitlines():
        if line.strip().startswith("c conflicts"):
            parts = line.split()
            for p in parts:
                if p.isdigit():
                    conflicts = int(p)
    if conflicts is not None:
        rec["conflicts"] = conflicts

    if status == "SAT":
        info = check(n, d, parse_model(text))
        rec["verified_model"] = bool(info["ok"])
        rec["min_out"] = info["min_out"]
        rec["narcs"] = info["narcs"]
        rec["outdeg"] = info["outdeg"]
        rec["indeg"] = info["indeg"]
        rec["two_cycles"] = info["two_cycles"]
        rec["triangles"] = info["triangles"]
        rec["arcs"] = info["arcs"]
    elif status == "UNSAT" and proof and proof_path.exists() and proof_path.stat().st_size > 0:
        try:
            drat = find_bin("drat-trim")
        except FileNotFoundError:
            rec["drat"] = "missing-binary"
        else:
            chk = subprocess.run(
                [str(drat), str(cnf_path), str(proof_path)],
                capture_output=True,
                text=True,
            )
            rec["drat"] = "VERIFIED" if "s VERIFIED" in (chk.stdout + chk.stderr) else (
                (chk.stdout + chk.stderr)[-300:]
            )
            rec["drat_bytes"] = proof_path.stat().st_size
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--d", type=int, required=True)
    ap.add_argument("--time", type=int, default=60)
    ap.add_argument("--indeg0", type=int, default=None)
    ap.add_argument("--exact-in", action="store_true")
    ap.add_argument("--no-sb", action="store_true")
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--u-from-1", type=int, default=None)
    ap.add_argument("--nplus1-from-2", type=int, default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--stable", action="store_true")
    args = ap.parse_args()
    extra = ["--stable"] if args.stable else None
    rec = run_one(
        args.n,
        args.d,
        args.time,
        args.indeg0,
        args.exact_in,
        sb=not args.no_sb,
        proof=args.proof,
        tag=args.tag,
        u_from_1=args.u_from_1,
        nplus1_from_2=args.nplus1_from_2,
        extra_args=extra,
    )
    print(json.dumps({k: v for k, v in rec.items() if k != "arcs"}, indent=2))
    if args.json_out:
        args.json_out.write_text(json.dumps(rec, indent=2))
        print("wrote", args.json_out)


if __name__ == "__main__":
    main()

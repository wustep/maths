#!/usr/bin/env python3
"""Run native CaDiCaL 3 / Kissat / drat-trim on a leftover CNF.

PySAT Cadical195 ASCII DRAT did not verify on the T5 36-clique.
Native CaDiCaL 3.0.1 writes binary DRAT; Heule drat-trim checks it.

  python3 native_sat.py certs/five_k32_n2_1.cnf --proof
  python3 native_sat.py certs/n1_k19_star5.cnf --solver kissat
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
BIN = HERE / "bin"


def parse_cadical(log: str) -> dict:
    sat = None
    if re.search(r"^s UNSATISFIABLE", log, re.M):
        sat = False
    elif re.search(r"^s SATISFIABLE", log, re.M):
        sat = True
    conflicts = None
    m = re.search(r"^c conflicts:\s+(\d+)", log, re.M)
    if m:
        conflicts = int(m.group(1))
    seconds = None
    m = re.search(r"^c total process time since initialization:\s+([0-9.]+)", log, re.M)
    if m:
        seconds = float(m.group(1))
    return {"sat": sat, "conflicts": conflicts, "seconds": seconds}


def parse_kissat(log: str) -> dict:
    sat = None
    if re.search(r"^s UNSATISFIABLE", log, re.M):
        sat = False
    elif re.search(r"^s SATISFIABLE", log, re.M):
        sat = True
    return {"sat": sat}


def parse_drat(log: str) -> dict:
    status = None
    if re.search(r"^s VERIFIED", log, re.M):
        status = "VERIFIED"
    elif re.search(r"^s NOT VERIFIED", log, re.M):
        status = "NOT VERIFIED"
    out = {"status": status}
    m = re.search(r"(\d+) of (\d+) lemmas in core", log)
    if m:
        out["lemmas_in_core"] = int(m.group(1))
        out["lemmas_total"] = int(m.group(2))
    m = re.search(r"(\d+) resolution steps", log)
    if m:
        out["resolution_steps"] = int(m.group(1))
    return out


def run_cadical(cnf: Path, proof: Path | None, log_path: Path,
                extra_args=None) -> dict:
    cadical = BIN / "cadical"
    cmd = [str(cadical)]
    if extra_args:
        cmd.extend(extra_args)
    cmd.append(str(cnf))
    if proof is not None:
        cmd.append(str(proof))
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    wall = time.time() - t0
    log = (proc.stdout or "") + (proc.stderr or "")
    log_path.write_text(log)
    rec = parse_cadical(log)
    rec["exit"] = proc.returncode
    rec["wall"] = wall
    rec["solver"] = "cadical-3.0.1"
    if rec["sat"] is None:
        if proc.returncode == 20:
            rec["sat"] = False
        elif proc.returncode == 10:
            rec["sat"] = True
    return rec


def run_kissat(cnf: Path, log_path: Path) -> dict:
    kissat = BIN / "kissat"
    t0 = time.time()
    proc = subprocess.run([str(kissat), str(cnf)], capture_output=True, text=True)
    wall = time.time() - t0
    log = (proc.stdout or "") + (proc.stderr or "")
    log_path.write_text(log)
    rec = parse_kissat(log)
    rec["exit"] = proc.returncode
    rec["wall"] = wall
    rec["solver"] = "kissat-4.0.1"
    if rec["sat"] is None:
        if proc.returncode == 20:
            rec["sat"] = False
        elif proc.returncode == 10:
            rec["sat"] = True
    return rec


def run_drat(cnf: Path, proof: Path, log_path: Path) -> dict:
    trim = BIN / "drat-trim"
    t0 = time.time()
    proc = subprocess.run(
        [str(trim), str(cnf), str(proof)],
        capture_output=True, text=True,
    )
    wall = time.time() - t0
    log = (proc.stdout or "") + (proc.stderr or "")
    log_path.write_text(log)
    rec = parse_drat(log)
    rec["exit"] = proc.returncode
    rec["wall"] = wall
    rec["bytes"] = proof.stat().st_size if proof.exists() else 0
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cnf")
    ap.add_argument("--solver", default="cadical", choices=("cadical", "kissat"))
    ap.add_argument("--proof", action="store_true")
    ap.add_argument("--trim", action="store_true")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args()
    cnf = Path(args.cnf)
    if not cnf.is_absolute():
        cnf = HERE / cnf
    stem = cnf.stem
    log_path = HERE / "certs" / f"{stem}.{args.solver}.log"
    report = {"cnf": str(cnf), "solver": args.solver}
    if args.solver == "kissat":
        report["kissat"] = run_kissat(cnf, log_path)
        report["sat"] = report["kissat"]["sat"]
    else:
        proof = HERE / "certs" / f"{stem}.native.drat" if args.proof else None
        report["cadical"] = run_cadical(cnf, proof, log_path)
        report["sat"] = report["cadical"]["sat"]
        if args.proof and proof is not None and proof.exists():
            report["drat_bytes"] = proof.stat().st_size
            report["drat"] = proof.name
            if args.trim or (report["sat"] is False):
                tlog = HERE / "certs" / f"{stem}.native.drat-trim.log"
                report["drat_trim"] = run_drat(cnf, proof, tlog)
    out = Path(args.json_out) if args.json_out else HERE / "certs" / f"{stem}.sat.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in report if k != "log"}, indent=2)[:2000])
    print("wrote", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

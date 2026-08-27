#!/usr/bin/env python3
"""Independent recomputation of q1 certificates. Does not import sat_extend."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pathutil
from gaplib import max_gap_dilates, shakan_lower, uniq_mod


def check_sat_upper(path: Path) -> list[dict]:
    bad = []
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    p, n = data["p"], data["n"]
    best = data["G_upper"]
    for row in data["rows"]:
        A = uniq_mod(row["A"], p)
        if len(A) != n:
            bad.append({"tag": "upper-n", "T": row["T"]})
            continue
        g, _ = max_gap_dilates(A, p)
        if g != row["g"] or g >= row["T"]:
            bad.append({"tag": "upper-g", "T": row["T"], "g": g})
    got_best = min(row["g"] for row in data["rows"])
    if got_best != best:
        bad.append({"tag": "upper-best", "g": got_best, "best": best})
    return bad


def check_sat_extend(path: Path) -> list[dict]:
    bad = []
    if not path.exists():
        return []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("witness") is None:
            continue
        p, n, A = rec["p"], rec["n"], rec["witness"]
        A2 = uniq_mod(A, p)
        if len(A2) != n:
            bad.append({"tag": "n", "p": p})
            continue
        g, _ = max_gap_dilates(A2, p)
        if g != rec.get("witness_g"):
            bad.append({"tag": "g", "p": p, "claimed": rec.get("witness_g"), "got": g})
        if rec.get("G_upper") is not None and g != rec["G_upper"]:
            bad.append({"tag": "G_upper", "p": p, "claimed": rec["G_upper"], "got": g})
        if rec.get("exact") and g != rec.get("G"):
            bad.append({"tag": "G", "p": p, "claimed": rec.get("G"), "got": g})
        if g + 1e-12 < shakan_lower(p, n):
            bad.append({"tag": "shakan", "p": p, "g": g})
    return bad


def check_constructions(path: Path) -> list[dict]:
    bad = []
    if not path.exists():
        return []
    for line in path.read_text().splitlines():
        rec = json.loads(line)
        p, A, g = rec["p"], rec["A"], rec["g"]
        gg, _ = max_gap_dilates(A, p)
        if gg != g:
            bad.append({"tag": "ctor-g", "p": p, "tagA": rec["tag"], "claimed": g, "got": gg})
        if gg + 1e-12 < shakan_lower(p, len(uniq_mod(A, p))):
            bad.append({"tag": "ctor-shakan", "p": p, "g": gg})
    return bad


def check_wronskian(path: Path) -> list[dict]:
    bad = []
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    for rec in data:
        if rec["deg_W"] > rec["bound_2k_1"]:
            bad.append({"tag": "W-deg", "p": rec["p"]})
        if rec["need_nm1"] > rec["bound_2k_1"] and not rec["k_ge_p"]:
            # Shakan comparison should hold at the actual m = G+1
            bad.append({"tag": "shakan-compare", "p": rec["p"]})
        rising = rec.get("rising")
        if rising and rising["remain_nz"] != 0:
            # at m = G+1 the hitting condition says w need not vanish
            # (m = sup g + 1, so w vanishes). remain_nz should be 0.
            bad.append({"tag": "rising-remain", "p": rec["p"], "nz": rising["remain_nz"]})
    return bad


def main():
    bad = []
    bad += check_sat_upper(pathutil.CERTS / "sat_upper_73.json")
    bad += check_sat_extend(pathutil.CERTS / "sat_extend.jsonl")
    bad += check_constructions(pathutil.CERTS / "constructions_q1.jsonl")
    bad += check_wronskian(pathutil.CERTS / "wronskian_slice.json")
    print(json.dumps({"n_failures": len(bad), "failures": bad[:20]}, indent=2))
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Enumerate involution-mates of a given Latin square by blocking SAT."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile

from encode_involution_mols import model_to_squares, parse_model_lits
from encode_mate import HALF, N, encode_mate, var_id
from verify_involution_mols import verify


def primary_assignment(square) -> list[int]:
    lits = []
    for r in range(HALF):
        for c in range(N):
            lits.append(var_id(r, c, square[r][c]))
    return lits


def enumerate_mates(family, kissat: str, limit: int, time_per: int) -> list:
    cnf = encode_mate(family)
    mates = []
    extra: list[list[int]] = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(limit):
            path = os.path.join(td, f"m{i}.cnf")
            model = os.path.join(td, f"m{i}.out")
            with open(path, "w") as f:
                comments = [f"enum i={i} extra_blocks={len(extra)}"]
                # dump base
                nvars = cnf._next - 1
                ncl = len(cnf.clauses) + len(extra)
                for line in comments:
                    f.write(f"c {line}\n")
                f.write(f"p cnf {nvars} {ncl}\n")
                for cl in cnf.clauses:
                    f.write(" ".join(str(x) for x in cl) + " 0\n")
                for cl in extra:
                    f.write(" ".join(str(x) for x in cl) + " 0\n")
            r = subprocess.run(
                [kissat, "-q", f"--time={time_per}", path],
                stdout=open(model, "w"),
                stderr=subprocess.DEVNULL,
                check=False,
            )
            text = open(model).read()
            if "UNSATISFIABLE" in text:
                return mates
            if "SATISFIABLE" not in text:
                raise RuntimeError(f"solver stopped without answer at i={i}")
            sq = model_to_squares(1, parse_model_lits(model))[0]
            ok = verify(family + [sq])
            if not ok["ok"]:
                raise RuntimeError(f"false mate at i={i}: {ok}")
            mates.append(sq)
            # block this primary assignment
            extra.append([-lit for lit in primary_assignment(sq)])
    return mates


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("family_json")
    ap.add_argument("--limit", type=int, default=32)
    ap.add_argument("--time", type=int, default=30)
    ap.add_argument("--kissat", default="./kissat")
    ap.add_argument("-o", "--output")
    args = ap.parse_args()
    with open(args.family_json) as f:
        payload = json.load(f)
    family = payload["squares"] if isinstance(payload, dict) else payload
    mates = enumerate_mates(family, args.kissat, args.limit, args.time)
    print(f"found {len(mates)} mates (limit {args.limit})")
    if args.output:
        with open(args.output, "w") as f:
            json.dump({"n_mates": len(mates), "mates": mates}, f)
            f.write("\n")


if __name__ == "__main__":
    main()

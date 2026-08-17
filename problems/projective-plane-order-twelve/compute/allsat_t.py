#!/usr/bin/env python3
"""Enumerate solutions of a t-MOLS involution CNF by blocking primary vars."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile

from encode_involution_mols import encode, model_to_squares, n_primary, parse_model_lits
from verify_involution_mols import verify


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("t", type=int)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--time", type=int, default=20)
    ap.add_argument("--kissat", default="./kissat")
    ap.add_argument("-o", "--output")
    ap.add_argument("--no-normalize", action="store_true")
    args = ap.parse_args()
    cnf = encode(args.t, normalize=not args.no_normalize)
    nprim = n_primary(args.t)
    sols = []
    extra: list[list[int]] = []
    with tempfile.TemporaryDirectory() as td:
        for i in range(args.limit):
            path = os.path.join(td, f"s{i}.cnf")
            model = os.path.join(td, f"s{i}.out")
            nvars = cnf._next - 1
            with open(path, "w") as f:
                f.write(f"p cnf {nvars} {len(cnf.clauses)+len(extra)}\n")
                for cl in cnf.clauses:
                    f.write(" ".join(str(x) for x in cl) + " 0\n")
                for cl in extra:
                    f.write(" ".join(str(x) for x in cl) + " 0\n")
            subprocess.run(
                [args.kissat, "-q", f"--time={args.time}", path],
                stdout=open(model, "w"),
                stderr=subprocess.DEVNULL,
                check=False,
            )
            text = open(model).read()
            if "UNSATISFIABLE" in text:
                print(f"complete after {len(sols)} solutions")
                break
            if "SATISFIABLE" not in text:
                print(f"timeout/unknown after {len(sols)} solutions")
                break
            sqs = model_to_squares(args.t, parse_model_lits(model))
            if not verify(sqs)["ok"]:
                raise RuntimeError(f"bad solution {i}")
            sols.append(sqs)
            # block primary assignment
            pos = []
            truth = {abs(x): x > 0 for x in parse_model_lits(model)}
            block = []
            for v in range(1, nprim + 1):
                if truth.get(v, False):
                    block.append(-v)
            extra.append(block)
            if (i + 1) % 10 == 0:
                print(f"found {i+1}", flush=True)
        else:
            print(f"hit limit {args.limit}")
    print(f"n={len(sols)}")
    if args.output:
        with open(args.output, "w") as f:
            json.dump({"n": len(sols), "complete": len(sols) < args.limit, "squares": sols}, f)
            f.write("\n")


if __name__ == "__main__":
    main()

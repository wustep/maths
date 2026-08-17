#!/usr/bin/env python3
"""For each reduced involution Latin square, SAT-search two orthogonal mates."""

from __future__ import annotations

import json
import os
import subprocess
import sys

from encode_involution_mols import parse_model_lits
from encode_two_mates import encode_two_mates, model_to_two
from verify_involution_mols import verify


def load_l0s(path: str) -> list:
    with open(path) as f:
        payload = json.load(f)
    if isinstance(payload, dict) and "squares" in payload:
        items = payload["squares"]
        # enum of families (each item is a list of squares) or a single family
        if items and isinstance(items[0][0][0], int):
            # list of 12x12 squares
            return items
        return [fam[0] for fam in items]
    return payload


def main() -> None:
    src = sys.argv[1]
    outdir = sys.argv[2] if len(sys.argv) > 2 else "certs/two_mates"
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    os.makedirs(outdir, exist_ok=True)
    l0s = load_l0s(src)[:limit]
    summary = []
    for i, L0 in enumerate(l0s):
        cnf_path = os.path.join(outdir, f"L0_{i}.cnf")
        out_path = os.path.join(outdir, f"L0_{i}.out")
        drat_path = os.path.join(outdir, f"L0_{i}.drat")
        cnf = encode_two_mates(L0)
        with open(cnf_path, "w") as f:
            cnf.dump(f, [f"two mates of enum L0 #{i}"])
        subprocess.run(
            ["./kissat", "-q", "--time=90", cnf_path, drat_path],
            stdout=open(out_path, "w"),
            stderr=subprocess.DEVNULL,
            check=False,
        )
        text = open(out_path).read()
        rec = {"i": i, "vars": cnf._next - 1, "clauses": len(cnf.clauses)}
        if "UNSATISFIABLE" in text:
            rec["status"] = "UNSAT"
            # verify DRAT
            v = subprocess.run(
                ["./drat-trim", cnf_path, drat_path, "-t", "60"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            rec["drat"] = "VERIFIED" if "s VERIFIED" in v.stdout else "FAIL"
        elif "SATISFIABLE" in text:
            rec["status"] = "SAT"
            two = model_to_two(parse_model_lits(out_path))
            rep = verify([L0] + two)
            rec["verified"] = rep["ok"]
            if rep["ok"]:
                with open(os.path.join(outdir, f"L0_{i}_t3.json"), "w") as f:
                    json.dump({"squares": [L0] + two}, f)
                    f.write("\n")
        else:
            rec["status"] = "UNKNOWN"
        print(rec, flush=True)
        summary.append(rec)
        # drop large CNF/DRAT if UNSAT verified, keep a pointer
        if rec.get("drat") == "VERIFIED":
            os.remove(cnf_path)
            # keep the drat? they can be big. keep for the first few, drop rest
            if i >= 3:
                os.remove(drat_path)
    with open(os.path.join(outdir, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")
    print("done", {s: sum(1 for r in summary if r["status"] == s) for s in ("UNSAT", "SAT", "UNKNOWN")})


if __name__ == "__main__":
    main()

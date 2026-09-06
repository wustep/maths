#!/usr/bin/env python3
"""Assemble a decision from a checkpoint file, so a crash before the final
JSON print loses nothing.  Reads DONE/FOUND/PROG lines written (flushed) by
slp_search --checkpoint.

Usage: python3 decide_from_checkpoint.py CKPT NTASKS STEPS name=value ...
  e.g. python3 decide_from_checkpoint.py ck13.txt 10609 13 20!=2432902008176640000 ...

Prints, for each target, the shortest program found (if any) and whether the
search is complete (all NTASKS tasks done).  A target with no FOUND line and a
complete search has tau > STEPS.  Exits non-zero if the search is incomplete.
"""
import json, sys

def main():
    ckpt, ntasks, steps = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    targets = []
    for a in sys.argv[4:]:
        name, val = a.split("=", 1)
        targets.append((name, int(val)))
    done = set(); found = {}; prog = {}
    for line in open(ckpt):
        p = line.split()
        if not p: continue
        if p[0] == "DONE": done.add(int(p[1]))
        elif p[0] == "FOUND":
            t, st = int(p[1]), int(p[2])
            if t not in found or st < found[t]: found[t] = st
        elif p[0] == "PROG":
            t, st = int(p[1]), int(p[2])
            j = line.index("{")
            prog[(t, st)] = json.loads(line[j:])
    complete = len(done) == ntasks
    out = {"checkpoint": ckpt, "steps": steps, "tasks_total": ntasks,
           "tasks_done": len(done), "complete": complete, "targets": []}
    for i, (name, val) in enumerate(targets):
        rec = {"name": name, "value": str(val)}
        if i in found:
            st = found[i]; rec["found_steps"] = st
            pr = prog.get((i, st))
            if pr:
                vals = [int(x) for x in pr["values"]]
                assert vals[0] == 1 and vals[-1] == val and len(set(vals)) == len(vals)
                rec["program"] = pr["values"]
        else:
            rec["found_steps"] = None
            rec["tau_gt" if complete else "undecided_within"] = steps
        out["targets"].append(rec)
    print(json.dumps(out, indent=1))
    sys.exit(0 if complete else 2)

if __name__ == "__main__":
    main()

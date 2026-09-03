#!/usr/bin/env python3
"""Verify straight-line program witnesses with exact integer arithmetic.

Usage:
  python3 verify_slp.py decide13.json [decide12.json ...]

For every target with a witness program, checks that the value list starts
at 1, that every later value is the sum, product, or (positive) difference of
two earlier values, that all values are distinct positive integers, and that
the last value equals the target.  Prints one line per target and a JSON
summary; exits non-zero on any failure.  Stdlib only.
"""
import json, sys

def check_program(values, target):
    vals = [int(v) for v in values]
    if vals[0] != 1:
        return False, "does not start at 1"
    if vals[-1] != target:
        return False, "last value is not the target"
    if len(set(vals)) != len(vals):
        return False, "repeated value"
    if any(v <= 0 for v in vals):
        return False, "non-positive value"
    for k in range(1, len(vals)):
        ok = False
        prev = vals[:k]
        for i in range(k):
            for j in range(i, k):
                a, b = prev[i], prev[j]
                if vals[k] in (a + b, a * b, abs(a - b)):
                    ok = True; break
            if ok: break
        if not ok:
            return False, f"value #{k} = {vals[k]} is not derivable"
    return True, "ok"

def main():
    bad = 0; summary = []
    for path in sys.argv[1:]:
        d = json.load(open(path))
        L = d["steps"]
        for t in d["targets"]:
            N = int(t["value"])
            if t["found_steps"] is None:
                summary.append({"file": path, "name": t["name"], "steps": L, "status": "not reachable within %d steps (search claim)" % L})
                continue
            ok, msg = check_program(t["program"]["values"], N)
            steps = len(t["program"]["values"]) - 1
            if ok and steps != t["found_steps"]:
                ok, msg = False, "step count mismatch"
            if ok and steps > L:
                ok, msg = False, "witness longer than the search bound"
            print(f"{path}: {t['name']} in {steps} steps: {msg}")
            summary.append({"file": path, "name": t["name"], "steps": steps, "status": "verified" if ok else "FAILED: " + msg})
            if not ok: bad += 1
    json.dump(summary, open("verify_summary.json", "w"), indent=1)
    print(f"{bad} failures")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()

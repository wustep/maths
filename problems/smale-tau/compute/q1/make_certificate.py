#!/usr/bin/env python3
"""Assemble certificate.json from the run outputs present in this folder."""
import json, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
cert = {"problem": "smale-tau", "quest": "q1", "definition": "tau(N) = least k with x_0 = 1, x_k = N, x_i = x_j o x_l (j, l < i), o in {+, -, *}"}
c9 = json.load(open(os.path.join(HERE, "count9.json")))
cert["reached_within_k_steps"] = c9["reached_cumulative"]
cert["nodes_per_depth_to_9"] = c9["nodes_per_depth"]
decisions = {}
def load_json(f):
    try:
        txt = open(f).read()
        if not txt.strip():
            return None
        return json.loads(txt)
    except (json.JSONDecodeError, OSError):
        return None   # in-progress or partial file

for f in sorted(glob.glob(os.path.join(HERE, "decide*.json"))):
    d = load_json(f)
    if d is None or "targets" not in d:
        continue
    for t in d["targets"]:
        name = t["name"]
        e = decisions.setdefault(name, {"value": t["value"], "shortest_found": None, "no_program_of_length_at_most": None, "program": None})
        if t["found_steps"] is not None:
            if e["shortest_found"] is None or t["found_steps"] < e["shortest_found"]:
                e["shortest_found"] = t["found_steps"]; e["program"] = t["program"]["values"]
        else:
            e["no_program_of_length_at_most"] = max(e["no_program_of_length_at_most"] or 0, d["steps"])
for name, e in decisions.items():
    lo = (e["no_program_of_length_at_most"] or 0) + 1
    hi = e["shortest_found"]
    if hi is not None and hi == lo:
        e["tau"] = hi
    elif hi is not None:
        e["tau_range"] = [lo, hi]
    else:
        e["tau_at_least"] = lo
cert["targets"] = decisions
cert["runs"] = {}
for f in sorted(glob.glob(os.path.join(HERE, "decide*.json"))):
    d = load_json(f)
    if d is None or "targets" not in d:
        continue
    cert["runs"][os.path.basename(f)] = {k: v for k, v in d.items() if k != "targets"}
json.dump(cert, open(os.path.join(HERE, "certificate.json"), "w"), indent=1)
print(json.dumps({k: (v.get("tau") or v.get("tau_range") or v.get("tau_at_least")) for k, v in decisions.items()}))

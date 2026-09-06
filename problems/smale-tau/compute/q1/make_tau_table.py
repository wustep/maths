#!/usr/bin/env python3
"""Compare the C and Rust tau tables (count mode, 9 steps, n <= 10266) with each
other and with the OEIS A173419 b-file, then write tau_table_10266.txt in
b-file format (n tau(n)).  Every n <= 10266 is reached within 9 steps
(Markstrom's "initial interval" 10266), so the table is exact."""
import json, sys
c = json.load(open("count9_10266.json")); r = json.load(open("check_count9_10266.json"))
assert c["tau_table_bound"] == r["tau_table_bound"] == 10266
ct, rt = c["tau"], r["tau"]
assert ct == rt, "C and Rust tables differ"
assert min(ct) >= 0, "some n <= 10266 not reached within 9 steps"
b = {}
for line in open("b173419.txt"):
    p = line.split()
    if len(p) == 2: b[int(p[0])] = int(p[1])
assert all(ct[n - 1] == b[n] for n in b), "b-file mismatch"
with open("tau_table_10266.txt", "w") as f:
    for n, t in enumerate(ct, start=1):
        f.write(f"{n} {t}\n")
from collections import Counter
print(json.dumps({"n_max": 10266, "matches_bfile_to": max(b), "histogram": dict(sorted(Counter(ct).items())), "first_n_with_tau_9": ct.index(9) + 1 if 9 in ct else None}))

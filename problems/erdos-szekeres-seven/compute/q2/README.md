# q2 — the 33-vertex signotope slice

Baek and Balko single out rank-3 signotopes as a natural relaxation of planar
point sets. Once the vertices are ordered, every four-set has at most one sign
change in its lexicographically ordered triple signs. Every planar point set
can be labeled this way, so an UNSAT certificate for 33 signotope vertices
without a convex 7-set would prove `ES(7) = 33`.

`encode.py` uses one sign variable per triple and one parity variable per
four-set. For a realizable four-set, odd parity means that one point is inside
the triangle of the other three. Every seven-set is required to contain such
a non-convex four-set. The full instance has 46,376 variables and 5,254,128
clauses; 4,272,048 of those are the 35-literal seven-set clauses. The two
audit scripts exhaust the Boolean clauses and test their geometric meaning on
2,222 exact, x-ordered coordinate quadruples.

The intended finished object is the generated DIMACS file, an UNSAT DRAT
proof, and successful replay by `drat-trim`. A SAT assignment is only a
signotope and is not necessarily realizable by points. A timeout is residue,
not an upper bound.

Generate the full instance with:

```bash
python3 encode.py --n 33 --k 7 --out es_33_7_signotope.cnf
```

The small regression in `run_all.sh` checks the clause generator and the known
`ES(5)` boundary when `kissat` is available in `PATH` or named by the
`KISSAT` environment variable. `RESULT.md` records the checked toy proof and
the measured walls at the next and full sizes.

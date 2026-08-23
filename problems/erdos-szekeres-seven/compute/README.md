# Compute — Erdős–Szekeres seven

Verifier plus certificate. Every claimed number needs an independent
check that runs from the files in this folder. SAT UNKNOWN is not a
bound; search residue is not a lower bound.

Replay everything currently in the folder with:

```bash
./run_all.sh
```

`verify_record.py` evaluates the published general formulas at `k=7` and
checks the interval `33 <= ES(7) <= 113`. `q1/` independently replays the
classical lower-bound witness: 32 exact integer points in general position
with no seven in convex position. This matches the published lower bound; it
does not improve it. `q2/` gives a compact signotope SAT encoding, exact
geometry and truth-table audits, and a DRAT-checked `ES(5)` smoke test. Its
full 33-vertex run ended `UNKNOWN`; `q2/RESULT.md` records the artifact hashes
and resource wall.

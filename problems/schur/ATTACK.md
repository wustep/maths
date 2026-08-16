# Attack log — S(7) lower bound

## 2026-08-16 — q1

- Searched for a 7-coloring of [1697]. No coloring found. Near-coloring with 2 violations recorded (the recovered `near_1697_two_violations.txt` is empty — the actual coloring bytes were not in the Add-File patch).
- Scripts recovered: `search_shifted_sat.py`, `search_almost_symmetric_pysat.py`, `search_orbit_minconflicts.py`, `search_seed_multipliers.py`, `repair_near_coloring.py`, `verify_coloring.py`.
- Lean stub: `lean/Schur1697SymmetryObstruction.lean`.
- Memory: commit `61e0369` — S(7) no 1697 coloring.

## 2026-08-16 — q2

- m=144 seed; still 2 violations. Scripts: `q2_alternate_template_search.py`, `q2_exact_sat.py`, `q2_seed_cegar.py`, `audit_q2_residue.py`.
- RESEARCH.md recovered: Rowley ancillary XLS could not be ingested; no 1696 specimen copied.

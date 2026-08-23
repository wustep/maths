# n=75 canonical rct4 SAT

This campaign searches for 150 points on the $75\times75$ grid in
Flammenkamp's `rct4` symmetry class. The shared encoder fixes the
anti-diagonal empty and selects one diagonal two-orbit and 37 four-orbits.

The audited formula has 996,434 variables and 2,398,895 clauses. The
`n73-best-embedding.txt` phase seed is a checked 146-point rct4 set translated
into the interior of the 75-grid; it has no bad lines but cannot be completed
without moving points. `search_small_repair.py` exactly exhausts candidates
that change at most two of its selected orbits while preserving every row and
column count.

Run metadata and the structural DIMACS audit are recorded here. Replay the
source witness, phase audit, formula audit, and any certificate with:

```sh
problems/three-in-line/compute/q4/run_all.sh
```

The SAT wrapper used Python 3.13 and `python-sat==1.8.dev24`. A solver timeout
is `UNKNOWN` residue, not a bound on $D(75)$.

As an encoder control, forcing all 36 orbit variables from the checked n=71
witness returned the identical coordinate file and SHA-256. At n=75,
CaDiCaL 1.9.5 reported UNSAT when at least 30 of the 37 phase-seed orbits were
required, after 97.97 seconds and 79,660 conflicts. This subsumes the recorded
minimums 31 through 34. No proof trace was emitted, so these JSON files are
precise solver residue rather than certified exclusions.

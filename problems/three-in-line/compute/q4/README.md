# n=75 canonical rct4 SAT

This campaign searches for 150 points on the $75\times75$ grid in
Flammenkamp's `rct4` symmetry class. The shared encoder fixes the
anti-diagonal empty and selects one diagonal two-orbit and 37 four-orbits.

The audited formula has 996,434 variables and 2,398,895 clauses. The
`n73-best-embedding.txt` phase seed is a checked 146-point rct4 set translated
into the interior of the 75-grid; it has no bad lines but cannot be completed
without moving points.

Run metadata and the structural DIMACS audit are recorded here. Replay the
source witness, phase audit, formula audit, and any certificate with:

```sh
problems/three-in-line/compute/q4/run_all.sh
```

The SAT wrapper used Python 3.13 and `python-sat==1.8.dev24`. A solver timeout
is `UNKNOWN` residue, not a bound on $D(75)$.

# R(5,5) / q4

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

This folder continues the leftover SAT after q3 closed every order-7
automorphism on 43 vertices. The encoder is q2's `orbit_sat.py`, unchanged.
A stored DRAT/DRUP is a restriction on a hypothetical graph. A timeout is
residue. A SAT model that decodes to a genuine $(5,5,43)$-graph would move
the lower endpoint; none is stored here unless `certs/q4_summary.json` says
otherwise.

## Leftover instances

After q2 and q3, a hypothetical $(5,5,43)$-graph can have automorphism-group
order with prime divisors only among 2, 3, and 5. The degree window
$18\le d\le 24$ and complementation ($k\leftrightarrow c-k$) reduce those
primes to 142 fixed-neighbour representatives: 86 of order 2, 42 of order 3,
and 14 of order 5. The five maximum-cycle formulas already timed out at five
minutes in q3; their CNF hashes are required to match q2/q3.

## Replay

The Python scripts need `python-sat`. The solver and checker are the pinned q2
builds: kissat 4.0.4 at commit
`8af8e56f174b778aef3aa45af9f739b2a5f492c2` and `drat-trim` at commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

```sh
python3 -m venv .venv
.venv/bin/pip install python-sat
../q2/build_tools.sh
./run_all.sh
```

Collected result: `certs/q4_summary.json`.

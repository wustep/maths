# R(5,5) / q4

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

A hypothetical $(5,5,43)$-graph cannot have an automorphism of cycle type
$5^6 1^{13}$ or $5^7 1^8$. The encoder is q2's `orbit_sat.py`, unchanged.
Complementation sends the fixed-neighbour count $k$ to $c-k$. The stored
proofs are:

| cycle type | checked $k$ | covers | certificate |
|---|---|---|---|
| $5^6 1^{13}$ | 2 | 2, 4 | `certs/proofs/p5_c6_k2.drat.gz` |
| $5^6 1^{13}$ | 3 | 3 | `certs/proofs/p5_c6_k3.drat.gz` |
| $5^7 1^8$ | 3 | 3, 4 | `certs/proofs/p5_c7_k3.drat.gz` |

Each compressed DRAT was checked by the pinned `drat-trim` build, then
replayed by regenerating the CNF and checking again.

Together with q2 and q3, a hypothetical $(5,5,43)$-graph can have
automorphism-group order with prime divisors only among 2, 3, and 5, and if
5 divides that order then the permutation is not of type $5^6$ or $5^7$.
This is a restriction on a hypothetical graph, not a bound on $R(5,5)$.

## Searches still incomplete

The five maximum-cycle representatives for orders 2, 3, and 5 remain
`UNKNOWN` (the order-5 maximum-cycle formula timed out at fifteen minutes
under `kissat --unsat`). The other leftover cycle types for those primes
are not exhaustively searched. These timeouts imply no further restriction.

No $(5,5,43)$-graph was decoded.

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

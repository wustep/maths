# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

A hypothetical $(5,5,43)$-graph cannot have an automorphism of cycle
type $5^4 1^{23}$ in which a fixed vertex is adjacent to 0 or 4 of the
four 5-cycles. The encoder is q2's `orbit_sat.py`, unchanged.
Complementation sends the fixed-neighbour count $k$ to $c-k$, so the
stored proof at $k=4$ covers $k=0$ as well.

| cycle type | checked $k$ | covers | certificate |
|---|---|---|---|
| $5^4 1^{23}$ | 4 | 0, 4 | `certs/proofs/p5_c4_k4.drat.xz` |

The compressed DRAT was checked by the pinned `drat-trim` build, then
replayed by regenerating the CNF and checking again. gzip of the same
bytes exceeds GitHub's blob limit; the stored file is `xz -9`.

Together with q2, q3, and q4, a hypothetical $(5,5,43)$-graph can have
automorphism-group order with prime divisors only among 2, 3, and 5,
and if 5 divides that order then the permutation is not of type
$5^6$ or $5^7$, and is not of type $5^4$ with a fixed vertex meeting
0 or 4 of the 5-cycles. This is a restriction on a hypothetical
graph, not a bound on $R(5,5)$.

## Searches still incomplete

All five maximum-cycle representatives for orders 2, 3, and 5 remain
`UNKNOWN` at thirty minutes under `kissat --unsat`. The other $k$
values on $5^4 1^{23}$, and the rest of the leftover 2/3/5 list, are
not exhaustively searched. These timeouts imply no further
restriction.

No $(5,5,43)$-graph was decoded.

## Replay

The Python scripts need `python-sat`. The solver and checker are the
pinned q2 builds: kissat 4.0.4 at commit
`8af8e56f174b778aef3aa45af9f739b2a5f492c2` and `drat-trim` at commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

```sh
python3 -m venv .venv
.venv/bin/pip install python-sat
../q2/build_tools.sh
./run_all.sh
```

Collected result: `certs/q5_summary.json`.

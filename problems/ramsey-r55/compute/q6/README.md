# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

A hypothetical $(5,5,43)$-graph cannot have an automorphism of cycle
type $5^5 1^{18}$ in which a fixed vertex is adjacent to 2 or 3 of the
five 5-cycles. The encoder is q2's `orbit_sat.py`, unchanged.
Complementation sends the fixed-neighbour count $k$ to $c-k$, so the
stored proof at $k=2$ covers $k=3$ as well.

| cycle type | checked $k$ | covers | certificate |
|---|---|---|---|
| $5^5 1^{18}$ | 2 | 2, 3 | `certs/proofs/p5_c5_k2.drat.gz` |

The trimmed DRAT was checked by the pinned `drat-trim` build, then
replayed by regenerating the CNF and checking again. gzip -9 is 57MB.

Together with q2, q3, q4, and q5, a hypothetical $(5,5,43)$-graph can
have automorphism-group order with prime divisors only among 2, 3, and
5, and if 5 divides that order then the permutation is not of type
$5^6$ or $5^7$, is not of type $5^4$ with a fixed vertex meeting 0 or
4 of the 5-cycles, and is not of type $5^5$ with a fixed vertex
meeting 2 or 3 of the 5-cycles. This is a restriction on a
hypothetical graph, not a bound on $R(5,5)$.

## Searches still incomplete

$5^5 1^{18}$ at $k=1$ remains `UNKNOWN` at sixty minutes. $5^3 1^{28}$
at $k=1$ and $k=3$, $3^{12}1^{7}$ at $k=6$, and $3^{13}1^{4}$ at $k=5$
timed out at thirty minutes. The five maximum-cycle order-2/3/5
representatives, the other $k$ values on $5^4$, and $3^{13}1^{4}$ at
$k=6$ were not re-run under the same 1800s config that already timed
them out. The rest of the leftover 2/3/5 list is unfinished. These
timeouts imply no further restriction.

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

Collected result: `certs/q6_summary.json`.

# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

None stored yet. The encoder is q2's `orbit_sat.py`, unchanged.
Independently replayed representatives skipped here: $5^6 1^{13}$
($k=2,3$), $5^7 1^8$ ($k=3$), and $5^4 1^{23}$ at $k=4$ (covers $k=0$).

Together with q2, q3, q4, and q5, a hypothetical $(5,5,43)$-graph can
have automorphism-group order with prime divisors only among 2, 3, and
5, and if 5 divides that order then the permutation is not of type
$5^6$ or $5^7$, and is not of type $5^4$ with a fixed vertex meeting
0 or 4 of the 5-cycles. This is a restriction on a hypothetical
graph, not a bound on $R(5,5)$.

## Searches still incomplete

The leftover after those four names is 138 representatives. q5 left
130 pending and 8 timeouts at thirty minutes (all five maximum-cycle
order-2/3/5 instances, the other $k$ values on $5^4$, and
$3^{13}1^{4}$ at $k=6$). Those eight are not re-run first under the
same config. Priority is $5^5 1^{18}$ (only 600s in q4), then the
remaining order-5 types that only saw three minutes of `--plain`, then
high-cycle order 3.

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

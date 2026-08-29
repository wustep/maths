# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

This folder continues the leftover automorphism SAT after the
independently replayed $5^6$ and $5^7$ exclusions. The encoder is
q2's `orbit_sat.py`, unchanged. Isolated SAT timeouts are not a
bound.

## Scope

q3 left automorphism-group primes 2, 3, and 5 on 43 vertices. q4
closed cycle types $5^6 1^{13}$ and $5^7 1^8$. Those three stored
proofs stay in `../q4/`. This folder skips them and searches the
remaining degree-feasible representatives, starting with
maximum-cycle order 2/3/5 and the leftover $5^4$, $5^5$, and
high-cycle order-3 types.

A stored DRAT here is a restriction on a hypothetical
$(5,5,43)$-graph. It is not a bound on $R(5,5)$ unless a
43-vertex colouring is decoded.

## Replay

The Python scripts need `python-sat`. The solver and checker are
the pinned q2 builds: kissat 4.0.4 at commit
`8af8e56f174b778aef3aa45af9f739b2a5f492c2` and `drat-trim` at
commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

```sh
python3 -m venv .venv
.venv/bin/pip install python-sat
../q2/build_tools.sh
./run_all.sh
```

Collected result: `certs/q5_summary.json`.

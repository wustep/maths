# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

Search in progress. A stored, independently replayed DRAT will be a
restriction on a hypothetical $(5,5,43)$-graph automorphism, not a
bound on $R(5,5)$. The encoder is q2's `orbit_sat.py`, unchanged.

Together with q2 through q6, a hypothetical $(5,5,43)$-graph can have
automorphism-group order with prime divisors only among 2, 3, and 5,
and if 5 divides that order then the permutation is not of type $5^6$
or $5^7$, is not of type $5^4$ with a fixed vertex meeting 0 or 4 of
the 5-cycles, and is not of type $5^5$ with a fixed vertex meeting 2
or 3 of the 5-cycles. q7's $5^5$ at $k=1$ kissat UNSAT is not
independently replayable. This is a restriction on a hypothetical
graph, not a bound on $R(5,5)$.

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

Collected result: `certs/q8_summary.json`.

# R(5,5) / leftover 2/3/5 SAT

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

No new independently replayed certificate. The encoder is q2's
`orbit_sat.py`, unchanged.

`kissat --unsat --seed=17` printed `s UNSATISFIABLE` for
$5^5 1^{18}$ at $k=1$ in 7575s. The trimmed DRAT is 3.9GB. That is
over GitHub's blob limit, so the proof is not stored. The
independent check of the trimmed file was stopped at wrap. Hashes
and sizes are in `certs/p5_c5_k1.json`. This is not a restriction
you can replay from the repo.

Together with q2, q3, q4, q5, and q6, a hypothetical $(5,5,43)$-graph
can have automorphism-group order with prime divisors only among 2, 3,
and 5, and if 5 divides that order then the permutation is not of type
$5^6$ or $5^7$, is not of type $5^4$ with a fixed vertex meeting 0 or
4 of the 5-cycles, and is not of type $5^5$ with a fixed vertex
meeting 2 or 3 of the 5-cycles. This is a restriction on a
hypothetical graph, not a bound on $R(5,5)$.

## Searches still incomplete

$5^5 1^{18}$ at $k=1$ has no stored proof. $5^2 1^{33}$ at $k=2$ and
$3^{12}1^{7}$ at $k=5$ timed out at sixty minutes. $5^3 1^{28}$ at
$k=3$, $3^{11}1^{10}$ at $k=5$, and $2^{20}1^{3}$ at $k=10$ were
stopped mid-run. The five maximum-cycle order-2/3/5 representatives
and the rest of the leftover 2/3/5 list are unfinished. These
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

There is no stored DRAT. `run_all.sh` regenerates the leftover case
list and writes `certs/q7_summary.json`. Collected result:
`certs/q7_summary.json`.

Small DRAT proofs for n=21, d=7 cubes that finished.

A 7-outregular graph on 21 vertices has 147 arcs, so some in-degree
is at least 7. The cubes that decide the exact statement are
k=|N⁻(0)| ∈ {7,…,13}.

Replay, from `compute/q2/` after `./build_solvers.sh`:

```
for f in certs/keep/ch-21-7-k*.drat; do
  cnf=${f%.drat}.cnf
  ./bin/drat-trim "$cnf" "$f" | tail -1
done
```

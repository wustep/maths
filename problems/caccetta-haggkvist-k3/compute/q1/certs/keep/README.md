Small DRAT proofs for n=18, d=6 cubes that finished quickly.

Replay, from `compute/q1/` after `./build_solvers.sh`:

```
for f in certs/keep/ch-18-6-k{6,7,8,9,10,11}.drat; do
  cnf=${f%.drat}.cnf
  ./bin/drat-trim "$cnf" "$f" | tail -1
done
for f in certs/keep/ch-18-6-k0-t{1,2,3,4,5}.drat; do
  cnf=${f%.drat}.cnf
  ./bin/drat-trim "$cnf" "$f" | tail -1
done
```

Also stored: `ch-18-6-k1-t{1..5}.{cnf,drat}`.

The exact statement at n=18 uses only k=6..11: a 6-outregular graph has
108 arcs, so some in-degree is at least 6. Those six DRATs are the
certificate. Cubes k=2..5 are also UNSAT (large proofs, regenerate
with `solve.py --n 18 --d 6 --indeg0 k --proof`). The whole k=1 cube
is UNSAT in 587s with a 1.207 GB DRAT (sha256 in `ch-18-6-k1.sha256`),
not stored. The k=0 search is unused.

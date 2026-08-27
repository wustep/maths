# n=18, δ⁺=6

The first order where the exact Caccetta–Häggkvist triangle statement
is not implied by Hoàng–Reed (r≤5) or by the published HKN threshold
0.3465.  A C₃-free 6-outregular oriented graph on 18 vertices would
disprove the conjecture.  An UNSAT DRAT proof of the encoding would
prove the exact statement at this order.

`encode.py` writes a DIMACS instance: oriented, no directed triangle,
out-regular of degree `d`, N⁺(0)={1,…,d}.  Cardinality uses Sinz
sequential counters (the parent `encode_ch.py` used binomial subsets).
`--indeg0 k` also fixes N⁻(0)={d+1,…,d+k} by relabelling.

Replay the small-n pairs and the stored F₄ certificate:

```
./build_solvers.sh
./run_all.sh
```

The n=18 attack is one cube per in-degree of vertex 0:

```
python3 run_cubes.py --n 18 --d 6 --time 300 --proof
```

A timeout on a cube is an incomplete search, not a bound.

Stored proofs live in `certs/keep/`: cubes k=6..11 and the
k=0, k=1 slices t=1..5. Cubes k=2..5 are unsatisfiable by kissat;
their proofs are large and are rebuilt by
`python3 solve.py --n 18 --d 6 --indeg0 k --proof`. The leftover
slice is k=0 with `|N⁺(1) ∩ U| = 6`.

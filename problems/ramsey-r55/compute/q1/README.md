# R(5,5) / q1

Families left open after the 2026-08-17 algebraic census: one-edge-flip
extensions of the 656 published `(5,5,42)`-graphs; Cayley graphs on the
four groups of order 44 and both groups of order 45; graphs with a
7-cycle automorphism.

Replay:

```
./run_all.sh
```

Parent replay (McKay 656, circulant 42/43, flips, Seidel):

```
cd .. && ./replay.sh
```

Collected certificate: `certs/q1_summary.json`.

No `(5,5)`-graph was found on 43, 44, or 45 vertices. The published
interval is still 43 ≤ R(5,5) ≤ 46. An isolated SAT timeout is not a
new bound.

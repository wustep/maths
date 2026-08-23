# q2 — three exact Parts rotation layers

This campaign expands the first spawn to

$$
G\cup\rho G\cup\rho^2G,
\qquad \rho=(7+i\sqrt{15})/8.
$$

The three layers contribute 509, 424, and 424 new exact points after
deduplication. `build.py` constructs all 1,357 vertices and rebuilds every
unit edge by exact all-pairs comparison. Search uses the same five-color CNF
and CaDiCaL binding as q1. `run_all.sh` independently redoes the exact edge
rebuild, checks the stored coloring, and invokes the C edge/color checker.

Search:

```bash
./run_search.sh
```

Replay:

```bash
./run_all.sh
```

## Result

The three-layer graph has 1,357 vertices and 6,860 unit edges. CaDiCaL found
a proper five-coloring in 0.025 seconds, with color-class sizes 298, 296, 278,
254, 231. The committed model passes the exact Python rebuild and the separate
C checker. Its restriction colors every add-only subgraph of the 848 points
contributed by the two rotated copies, excluding all $2^{848}$ such subsets as
six-chromatic witnesses. The combined family with q1's separate 677-point
reserve was not searched.

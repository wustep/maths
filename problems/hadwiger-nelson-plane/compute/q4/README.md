# q4 — fourth exact Parts rotation layer

This campaign adjoins a genuinely new fourth rotation layer to q3's entire
combined graph. Starting from the 2,010-vertex union of the Parts graph, its
677-point reserve, and the first three rotation layers, it adds

$$
\rho^3G,\qquad \rho=(7+i\sqrt{15})/8.
$$

Of the 509 source vertices, 85 already occur in the combined graph and 424
are new. `build.py` reconstructs those points exactly. It retains q3's
already-replayed induced edges and compares every new point with every
earlier point in exact arithmetic, thereby rebuilding every edge incident to
the extension.

Search:

```bash
./run_search.sh
```

Full replay starts in the parent directory, where q1–q3 first verify the old
induced graph and q4 then independently reconstructs the extension:

```bash
cd ..
./run_all.sh
```

## Result

The exact graph has 2,434 vertices and 13,975 unit edges. The fourth layer
contributes 424 new vertices and 2,209 edges incident to them. CaDiCaL found
a proper five-coloring in 1.13 seconds, with color-class sizes 553, 430, 449,
522, and 480. The committed model passes the exact Python extension rebuild
and the separate C edge/color checker.

This is residue, not a lower bound. The model restricts to every subgraph, so
it covers arbitrary deletion of the 509 base vertices together with any
subset of the 1,925 non-base vertices. It does not cover points beyond this
reserve, deletion-and-replacement constructions using new coordinates, or
another algebraic family.

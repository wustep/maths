# q3 — combined exact Parts spawn

This campaign merges both exact finite families already replayed:

- q1's Parts graph plus its 677-point radius-2.55 reserve;
- q2's union $G\cup\rho G\cup\rho^2G$.

After exact deduplication the combination adds 1,501 distinct points to the
509-vertex base. It has 2,010 vertices. The two induced pieces already contain
all internal edges; `build.py` checks all $653\times824$ pairs between their
disjoint added parts with exact field arithmetic and finds the remaining 50
cross edges.

Search:

```bash
./run_search.sh
```

Full replay should be run from the parent `compute/` directory so q1 and q2
first independently rebuild the two pieces. This folder's replay then checks
the exact union, every cross edge, and the stored coloring with Python before
using the separate C edge/color checker.

```bash
cd ..
./run_all.sh
```

## Result

The combined graph has 2,010 vertices and 11,766 unit edges. CaDiCaL found a
proper five-coloring in 0.18 seconds, with color-class sizes 405, 386, 407,
403, 409. Exact decomposition replay and the separate C checker accept the
committed model. It restricts to every graph formed by adding an arbitrary
subset of the 1,501 distinct non-base points, excluding all $2^{1501}$ such
add-only candidates as six-chromatic witnesses.

This is residue, not a lower bound. The finite exclusion does not cover
deletions from Parts' 509 vertices, a fourth rotation layer, lattice points
outside the retained reserve, or another algebraic family.

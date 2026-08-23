# q1 — exact Parts spawns

This campaign starts from Parts' published 509-vertex graph and builds two
finite exact-coordinate supergraphs.

- `rho_union` is the union of the graph with its image under Parts' rotation
  $\rho=(7+i\sqrt{15})/8$.
- `reserve_union` adds the entire named radius-2.55 reserve: every unused
  point retained by the source enumeration in Parts' unrotated or rotated
  lattice disk, each having at least four exact unit neighbors in the base
  graph. `reserve_source.json` is the finite source table copied from the
  independently run `unit-distance-509` campaign; `extract_reserve.py`
  reconstructs all 677 exact coordinates from it. The larger universe
  enumeration was not rerun in this process.

The search asks whether either supergraph is 5-colorable. A stored coloring
kills not only the full graph but every subgraph formed by deleting added
vertices. Coordinates are in `parts509.vtx`, sourced from the Polymath data
archive via the Lean formalization repository; `udg.py` rebuilds every unit
edge in $\mathbb Q(\sqrt3,\sqrt5,\sqrt{11})$.

Search setup:

```bash
python3 -m venv .venv
.venv/bin/pip install python-sat
./run_search.sh
```

Certificate replay does not require PySAT:

```bash
./run_all.sh
```

The Python verifier reconstructs every exact edge from coordinates and checks
the stored colors. The C verifier independently checks the edge-list/coloring
certificate. A SAT result is a killed finite candidate, not a lower bound.

## Result

Both candidates are five-colorable.

| graph | vertices | unit edges | SAT time | color-class sizes |
| --- | ---: | ---: | ---: | --- |
| $G\cup\rho G$ | 933 | 4,651 | 0.015 s | 211, 203, 203, 165, 151 |
| $G$ plus all 677 reserve points | 1,186 | 7,440 | 2.89 s | 259, 251, 225, 220, 231 |

Times are from Python 3.13.5, python-sat 1.9.dev15, and its CaDiCaL 1.9.5
binding. They are only a search log; the committed colorings are the
certificates. Since the second coloring restricts to every subgraph obtained
by deleting reserve points, it excludes all $2^{677}$ add-only subsets as
six-chromatic witnesses. This says nothing about deleting base vertices,
introducing other coordinates, or composing different layers.

# Compute — 509-vertex unit-distance graph

## Certificate replay

```
python3 -m venv .venv && .venv/bin/pip install sympy python-sat
# compile drat-trim if the binary is missing:
#   gcc -O2 -o drat-trim /path/to/drat-trim.c
./run_verify.sh
```

`run_verify.sh` rebuilds the unit-distance graph from `509_parts.vtx` (must get 509 vertices and 2442 edges) and checks `color509.drat` against a freshly generated 4-coloring CNF.

Vertex-criticality of a degree-4 deletion:

```
.venv/bin/python check_gv_coloring.py 509_parts.vtx coloring_Gminus_310.txt --missing 310
```

## Sources of coordinates

- `509_parts.vtx` — Parts’ 509-graph, from [vasnesterov/HadwigerNelson](https://github.com/vasnesterov/HadwigerNelson/blob/master/vtx/509_parts.vtx), originally the Polymath16 fifteenth thread.
- `510_heule.vtx` — Heule’s 510-graph, same repository / CNP-SAT. Control only.

Do not invent coordinates. New points used in searches are lattice points \((a+b\sqrt{33}+ic\sqrt{3}+id\sqrt{11})/12\) or their rotation by \(\rho=\exp(i\arccos(7/8))\), as in Parts arXiv:2010.12665.

## What the search did

See `search_summary.json`, `../ATTACK.md`, and `../WALKTHROUGH.md`. No graph smaller than 509 was obtained.

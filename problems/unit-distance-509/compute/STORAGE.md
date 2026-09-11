# SAT proof storage

`color509.drat` and `color509.core.drat` are not in the git tree.
The graph is `509_parts.vtx`. The coloring summary is
`color509.json` (UNSAT, triangle `(0,149,152)`).

## Regenerate the 4-coloring proof

```
python3 -m venv .venv && .venv/bin/pip install sympy python-sat
.venv/bin/python color_sat.py 509_parts.vtx --proof color509.drat
```

Then `./run_verify.sh` rebuilds the unit-distance graph and, if
`color509.drat` is present, checks it with `drat-trim` against a
fresh CNF. Without the DRAT, `run_verify.sh` still checks the 509
vertices / 2442 edges and stops there.

There is no Release URL for the old proof files.

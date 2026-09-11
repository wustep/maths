Cube index for exact Caccetta–Häggkvist triangle leftover orders
n=73 through n=108 (1026 cubes). First remaining hole n=109. The
DRAT bytes are not in the git tree; see `../../STORAGE.md`.

A d-outregular oriented graph has n d arcs, so some in-degree is
at least d. Relabel that vertex as 0. The exact statement reduces
to cubes k=|N⁻(0)| ≥ d. Each cube was UNSAT with a DRAT. Local
replay regenerates the CNF from `encode.py` and checks a
regenerated proof; do not trust leftover `certs/*.cnf` scratch
files.

```
cd problems/caccetta-haggkvist-k3/compute/q4
./build_solvers.sh
./run_all.sh
```

The index is `replay.json` after a successful `verify_keep.py`.
Circulant soundness (cyclic degree, not a counterexample) is
`soundness_n73_d24.json`.

A separate F₄ flag-algebra certificate with the CKLS 2015 fork
(`c = 0.34640`) is `f4_or_new_certificate.json`. Replay:

```
python3 verify_q4_certificate.py certs/keep/f4_or_new_certificate.json
```

Independent F-coordinates (no import of that verifier):

```
python3 dump_f_coords.py
```

writes `f_coords_0.3464.json`.

# SAT proof storage

The cube DRATs are not in the git tree. A clone ships the encoder,
`solve.py` / `run_cubes.py`, and the JSON cube index
(`certs/keep/*summary.json`, `replay*.json`). That index is the
committed record of which `(n,d,k)` cubes were checked. It is not
itself a DRAT.

## Regenerate one cube

From the quest folder, after `./build_solvers.sh`:

```
python3 solve.py --n N --d D --indeg0 K --proof --keep
```

`encode.py` writes a fresh CNF; kissat writes
`certs/keep/ch-N-D-kK.drat`. Scratch `certs/*.cnf` and
`certs/*.drat` stay gitignored.

## Replay a local keep tree

```
python3 verify_keep.py
```

`run_all.sh` still checks the F₄ certificate and the encoder
regression. If `certs/keep/` has no `*.drat`, `verify_keep.py`
leaves the committed JSON alone and does not claim a SAT replay.

There is no Release tarball URL for these proofs. A later upload
can be linked here when one exists.

Worktrees: keep one local `certs/keep/` and point the others at it
if you must share proofs. Do not copy the tree into every campaign.

# Compute

Stdlib + `compute/.venv` (`python-sat`, `numpy`). System Python has
matplotlib for the figure.

`q1/` is a later search (rising-factorial degrees, SAT past 71,
more families). Replay `q1/run_all.sh`. It does not change the
published constant 2.

Independent checks (do not claim a dent):

```bash
cd problems/long-gap-dilate
compute/.venv/bin/python compute/verify.py
compute/.venv/bin/python compute/verify_sat_witnesses.py
compute/.venv/bin/python compute/enum_diagonal.py
```

Exact `G(p, n=round sqrt p)` (SAT; enum agrees through p=41):

```bash
compute/.venv/bin/python compute/sat_census.py --pmax 47 --out compute/certs/sat_G.jsonl
```

Constructions / local-search upper bounds, n=3 and n=4 enumerations,
Singer, greedy hitting sets: `eval_constructions.py`, `run_local_batch.py`,
`n3_scan.py`, `enum_G.py --n 4`, `eval_singer.py`, `greedy_hit.py`.

`verify.py` brute-force checks Shakan on every nonempty proper subset of
`F_p` for p=5,7,11,13 and on the listed constructions up to p=80.

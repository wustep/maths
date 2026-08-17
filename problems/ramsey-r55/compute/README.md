# Compute — R(5,5)

Replay the deterministic residue (no SAT required):

```
gcc -O3 -std=c11 -o circulant_census circulant_census.c
gcc -O3 -std=c11 -o extend_check extend_check.c
gcc -O3 -std=c11 -o dump_circulants dump_circulants.c
gcc -O3 -std=c11 -o extend_one extend_one.c
python3 verify_mckay.py
./extend_check refs/r55_42some.g6
./circulant_census 43
python3 py_circulant.py 43
```

`kissat` is a local build of 4.0.4 (`build_kissat.sh`). Involution test: `cnf/involution17.cnf` must be SAT and decode to a `(5,5,17)`-graph via `decode_involution.py`.

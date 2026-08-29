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

The 2026-08-27 search lives in `q1/`:

```
cd q1 && ./run_all.sh
```

The 2026-08-29 search lives in `q2/`. It adds the complete two-edit extension
ball, prime-order automorphism cycle-type proofs, and a certified radius-6
ball around a score-2 near graph:

```sh
cd q2
PATH="$PWD/../../../../.venv/bin:$PATH" ./run_all.sh
```

The 2026-08-29 follow-up lives in `q3/`. It closes every order-7
automorphism cycle type on 43 vertices with checked DRAT/DRUP certificates.
The published interval remains $43\le R(5,5)\le46$.

```sh
cd q3
./run_all.sh
```

The later 2026-08-29 leftover search lives in `q4/`. It certifies that a
hypothetical $(5,5,43)$-graph has no automorphism of cycle type $5^6 1^{13}$
or $5^7 1^8$. The published interval remains $43\le R(5,5)\le46$.

```sh
cd q4
./run_all.sh
```

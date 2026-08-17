# Compute — Seymour second-neighborhood

Python 3.13 venv: `compute/.venv` (`python-sat`, `ortools`).

```bash
# labeled Pisa census n<=7 (OpenMP)
gcc -O3 -march=native -fopenmp -std=c11 -o enum_pisa enum_pisa.c
./enum_pisa 6
./enum_pisa 7

# n=8 type census over nauty geng representatives
gcc -O3 -march=native -o enum_pisa_geng enum_pisa_geng.c
/path/to/geng -q 8 | ./enum_pisa_geng

# replay constructions and SAT witnesses
.venv/bin/python check_known.py
.venv/bin/python verify_witnesses.py
.venv/bin/python verify_census.py
```

Certificates live in `certs/`. A graph given by `arcs` or ternary `code` is Pisa iff `seymour.is_pisa` returns true.

Independent of the solvers: `seymour.py` recomputes first/second neighbourhoods by bitmasks.

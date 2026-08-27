# Compute

```
./run_all.sh
```

Requires numpy, scipy, mpmath, matplotlib (`/tmp/ucvenv` if present).

| script | what |
| --- | --- |
| `solve_published.py` | mpmath dps=80 replay of φ, c*, Liu c₅ |
| `verify.py` | official checks for claimed 0.38285; writes `verify.json` |
| `first_crossing.py` | c(β) on the {b,1} ray for Example 4 and 5 |
| `plot_crossing.py` | `../figures/ray_crossing.png` |
| `hunt_mixtures.py` | 3-atomic / 2-mixture residue at (β,c)=(0.20, 0.38285) |
| `enum_small.py` | union-closed families on n≤4 (min abundance = 1/2) |
| `q1/` | pure Example 4 on {b,1}; claimed 0.38304; `q1/run_all.sh` |

Papers used tonight live in `refs/`. The 2026-08-27 replay of the new constant is `q1/run_all.sh`.

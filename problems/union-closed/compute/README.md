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
| `q2/` | 2-sample ceiling on {b,1}; mixes / 3-atomic / new protocols; constant unchanged; `q2/run_all.sh` |
| `q3/` | tighter 9,000×7,000 certificate on {b,1}; claimed 0.38305; `q3/run_all.sh` |

Papers used tonight live in `refs/`. The 2026-08-27 replay of the
current printed constant is `q3/run_all.sh`; q1 supplies the analytic
crossing and q2 supplies the 2-sample-class ceiling.

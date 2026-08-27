# compute — simon-ionization-excess

Replay of published upper bounds on Nc(Z). This folder does not claim
a new ionization bound.

```bash
sh run_all.sh
```

`ionization_bounds.py` rebuilds the Hundertmark–Pattakos–Schulz
closed form for b(3), checks the two decimal windows printed in
arXiv:2504.18487, and writes Lieb / Nam / HPS values at
Z = 1, 5, 6, 36, 118. Nam first undercuts Lieb at Z = 6. The s=3
line first undercuts the s=2 line at integer Z = 36 (paper remark:
Z ≥ 35.8).

Output: `record.json`.

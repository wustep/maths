# Exact Cohn–Elkies d=2 certificate

Replay:

```
/tmp/ce-venv/bin/python verify.py
```

or `./run_all.sh` (rebuilds the certificate, then verifies).

`certs/ce_d2_m5.json` is the exact auxiliary function:
radial profile polynomials `F(t)`, `hatF(t)` in `t = 2π|x|²`, times the
Gaussian `exp(-π|x|²)`. Theorem 3.2 of Cohn–Elkies 2003 then gives

    center density ≤ R/(8π),   R = 3627599/500000 = 7.255198.

That meets Cohn–Elkies Table 3 (0.28868) and is strictly below the
printed Table 4 value `2πr² = 7.25520`. It is not a magic function:
the hexagonal target is `4π/√3 ≈ 7.2551974569`.

# Replay

Do not claim the Landau–Ramanujan density. The scripts never use it.

## What is certified

`G(n) < 2√2 n^{1/4} − 3` for every integer `2 ≤ n ≤ 1.024e15`
except `n ∈ {3, 6, 21, 91}`. (`n=1` makes the right-hand side negative.)

Jameson’s `a=2` has **no** exceptions on `1..5e6` (exhaustive table).

## Independent checks

```bash
# Exact G(n) from a two-square table. Exceptions must be {1,3,6,21,91}.
python3 compute/verify_exhaustive.py --N 2000000 --out compute/exhaustive_a3_2e6.json

# Stored witnesses for every danger-zone top with m <= 250.
python3 compute/verify_a3_cert.py compute/a3_cert_m250.json

# Same, m <= 2000 (gunzip first). About 1e6 witnesses.
# python3 -c "import gzip,shutil; gzip.open('compute/a3_cert_m2000.json.gz')"  # or gzip -dk
# python3 compute/verify_a3_cert.py compute/a3_cert_m2000.json

# Re-run the danger-zone search with no stored witnesses.
python3 compute/certify_a3.py --m-max 8000 --out compute/a3_summary_m8000.json
```

`certify_a3.py` enumerates the integer danger zone of RESEARCH.md
(ladder tops `n=u^2+m^2+1` with `2u=m^2+k` and `2m-2 ≤ k ≤ 3m+2`)
and searches for a lattice point with leftover `< Φ−3`.

## Plot

```bash
python3 compute/plot_gaps.py 2000000 figures/gap_ratios.png
```

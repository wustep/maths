# SuperGrok 2026-08-17

Weekly SuperGrok pool, `grok-4.6` xhigh. No Extra Usage purchase.

## Finished

### P15 Chowla cosine — `problems/chowla-cosine`

Verified: for every n ≥ 1 and every n-element set of positive integers,

    min_x  ∑_{a ∈ A} cos(a x)  ≤  − n^{1/7} / 18.

Replay: `cd problems/chowla-cosine && ./compute/run_all.sh` (exit 0).

This names the constant in Bedert §7's polynomial bound. It does **not** beat Bedert v3's exponent `n^{1/5−o(1)}`. Soft spot: the Young/split constants 3 and 14 in `compute/CONSTANTS.md`.

### P07 Sidon second term — `problems/sidon-second-term`

Verified Hou–Zhao arXiv:2607.01169v2 (C < 0.9435) independently, then the same eight kernels at L=6:

    F(N) ≤ √N + 0.94349251 N^{1/4} + O(1)

with √(ab) = 0.9434925085, which is 8.22×10^{-8} below Hou–Zhao's exact γ0. Replay:

```
python3 problems/sidon-second-term/compute/verify_houzhao.py
python3 problems/sidon-second-term/compute/verify_certificate.py problems/sidon-second-term/compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 problems/sidon-second-term/compute/verify_beat_hz.py
```

Does **not** change the four-decimal statement 0.9435. Same lemma, longer boundary. Residue if the bar is a new method or a 0.9434-level constant.

## In flight

- P29 unit-distance 509
- Landau 4 (`n^2+1` primes)
- P14 two-squares gap (started after P07/P15 finished)
- P16 cosine zeros (started after P07/P15 finished)

Keep launching leftover 50-list problems until about 10% of the weekly SuperGrok pool remains, then wrap. Do not buy usage.

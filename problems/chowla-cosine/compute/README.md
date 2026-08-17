# Compute — Chowla cosine, explicit c = 1/18

```
./run_all.sh
```

Expected: last line `ALL OK`, exit 0.

| script | role |
|---|---|
| `verify_lemma72.py` | exact 32-window check of Bedert Lemma 7.2 in `Q(sqrt(2))` |
| `lemma71_bounds.py` | arithmetic pack of the Young/split constants |
| `track_constants.py` | builds `certificate.json` |
| `verify_certificate.py` | rebuilds `Cstar`, checks `2048 Cstar <= 18^7` |
| `optimize_aux.py` | float search of `(alpha, beta, phi)`; did not beat Bedert |
| `qsqrt2.py`, `aux_rho.py` | exact arithmetic |

Claim (not the square-root conjecture): for every `n >= 1` and every
`n`-element set of positive integers,

```
min_x sum_{a in A} cos(a x)  <=  - n^{1/7} / 18.
```

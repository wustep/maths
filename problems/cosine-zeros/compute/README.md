# Compute — cosine zeros (P16)

```
./run_all.sh
```

Expected: last line `ALL OK`, exit 0.

| script | role |
|---|---|
| `check_kernel.py` | Bedert kernel `φ` has `P² α ∈ ℤ`, `|α|≤4`, `φ≥0`, `φ(0)=4` for `P=1..24` |
| `check_si_group.py` | sampled Si sums sit under `12(1+log K)` |
| `track_bedert.py` | prints `log F(d) / (d log d)` from Erdélyi+Bedert majorants |
| `verify_certificate.py` | rebuilds `F`, checks `1+log K̃ ≤ 2X` and `log F ≤ 200 d log d` |
| `hankel_det.py` | residue: 0-1 Hankel max-dets match Hadamard order (no exponent gain) |
| `search_prefix.py` | residue: `|E(g)|` for structured prefixes vs `Θ(log m/√m)` (not in `run_all`) |
| `trig.py` | shared evaluation |

Claim (not a new exponent, not a new construction): for `0-1` cosine sums,
`Z(N) ≥ log log N / (200 log log log N)` whenever the right-hand side is at least `4`.
This names the constant in Bedert Theorem 1.3. It does not beat
`(log log N)^{1-o(1)}` and it does not beat `O((N log N)^{2/3})`.

# Explicit constants for Bedert's cosine-zero bound (S = {0,1})

All logs are natural. `d` is the number of zeros of `g` in `(0, π)`.
`N = |A| = g(0)`. `Z(N)` counts zeros in `[0, 2π]`, so `Z ≥ d`.

## Published inputs

1. **Erdélyi, arXiv:1702.05823, Theorem 1.7.** For integers `λ1 < ⋯ < λm` and complex `a_j`,
   ```
   ∫_0^{2π} |∑ a_j e^{i λ_j t}| dt  ≥  (1/30) ∑ |a_j|/j.
   ```
   On `[0,1]` with `e(t) = exp(2π i t)` this is `1/(60π)` times the same sum.
   Paying `1/2` from the cosine-to-exponential conversion (`α_k = c_j/2`) we use
   ```
   c_L = 1/(120 π)
   ```
   as the constant in `||g̃||_{L¹[0,1]} ≥ c_L P^{-2} log N`.

2. **Erdélyi Lemma 3.7.** `m = ⌊32 d log log(2d+3)⌋`, `d_m := lcm[1..m] < 3^m`
   (Nair, cited as Erdélyi [65]).

3. **Erdélyi Lemma 3.8 on the algebraic lift.** A `{0,1}`-cosine polynomial
   lifts to a self-reciprocal `G` with coefficients in `{0,1,2}`
   (Bedert §4, footnote: the middle coefficient lies in `2S`). We take
   `S = {0,1,2}`, `M = 2`, `|S| = 3`:
   ```
   log q ≤ X := 60π · 16^{2d+1} · (2d+1)^{d+3/2} · L,
   L := 5^{4m+2} + 6d+3 ≤ 2 · 5^{4m+2}.
   ```

4. **Kernel.** `φ(t) = (2/P ∑_{n=0}^{P-1} cos(2π n t))² ≥ 0`, `φ(0) = 4`.
   Fourier coefficients of `φ` lie in `P^{-2} ℤ ∩ [-4, 4]`
   (`compute/check_kernel.py`). Hence so do the coefficients `c_j` of
   `g̃ = g φ` after the interior-periodisation computation of Bedert §3.

## Variation of the cotangent correction

Let `ψ(t) = (1/2) cot(t/2) − 1/t` on `(0, π]`. Then `tan u > u` on `(0, π/2]`
gives `ψ < 0`, and `ψ'(t) = (sin²(t/2) − (t/2)²)/(t² sin²(t/2)) < 0`.
So `ψ` decreases from `0` to `ψ(π) = −1/π`, `‖ψ‖_∞ = 1/π`, `V(ψ) = 1/π`.
Integration by parts yields, for `n ≥ 1` and `x ∈ (0, π]`,
```
|∫_0^x ψ(t) sin(n t) dt| ≤ 4/(π n).
```
Together with `|∫ (1/2) cos(n t) dt| ≤ 1/(2n)` this is Bedert Lemma 3.3 with
constant `2/n` on the original scale, hence
```
|∫_0^x D_n(2π t) dt − Si(2π n x)/(2π)| ≤ 1/(π n).
```

## Si-sum (Bedert Lemmas 3.4–3.5)

For `y' > y > 1`,
```
|∫_y^{y'} (sin t)/t dt| ≤ (2/y) min(1, |y'−y|).
```
Grouping the Bedert (18) partition by unit intervals in the `n_j x`-line and
using `sup |Si| < 2` gives
```
|∑_j ∫_{n_{j-1} x}^{n_j x} (sin t)/t dt| ≤ 12 (1 + log K̃).
```

## Proposition 3.1, numerical form (S = {0,1})

- `K̃ ≤ 5 P K` (each of `K` intervals contributes `≤ 4P` boundary frequencies).
- `log K ≤ X + 8 P log 3` (short-interval singletons; checked `8 P log 3`
  dominates `D log 2` with `D < 2 · 3^m + 2d`).
- `1 + log K̃ ≤ 2X` for every `d ≥ 2` (`verify_certificate.py`).
- `sup |G| ≤ 12 (1 + log K̃)`.
- `‖g̃‖_1 ≤ 4(d+1) sup|G| = 48 (d+1) (1 + log K̃)`.
- Lower bound `‖g̃‖_1 ≥ log N / (120 π P²)`.

Therefore
```
log N ≤ 5760 π (d+1) P² (1 + log K̃) ≤ F(d),
F(d) := 11520 π (d+1) · 3^{2m} · X.
```

## Inversion

`verify_certificate.py` checks `log F(d) ≤ 200 d log d` for `4 ≤ d ≤ 2000`.
Hence any `0-1` cosine `N`-sum with at most `d ≥ 4` zeros in `(0, π)` satisfies
`log log N ≤ 200 d log d`, so
```
Z(N) ≥ log log N / (200 log log log N)
```
whenever the right-hand side is at least `4`.

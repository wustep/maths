# Attack log — zeros of integer cosine sums

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House rules: write only here; no git; cite what we beat.
- Adjacent tonight: `problems/chowla-cosine` extracted an explicit `K(n) ≥ n^{1/7}/18` from Bedert's Chowla paper. Do not touch that folder.
- Green 100 #82 (Dec 2025 `open-problems.pdf`, Harmonic analysis, p. 38–39): for `|A|=n`, how many `θ ∈ ℝ/ℤ` have `∑_{a∈A} cos(aθ) = 0`? Littlewood [212, Problem 22] guessed `n-1` or not much less.
- Published record fetched tonight:
  - Construction / upper barrier: Borwein–Erdélyi–Ferguson–Lockhart, *Ann. of Math.* 167 (2008), `O(n^{5/6} log n)` zeros. Optimised independently by Konyagin, *Math. Notes* 108 (2020) and Juškevičius–Sahasrabudhe, *Bull. Lond. Math. Soc.* 53 (2021) / arXiv:2005.01695v3, to `O((n log n)^{2/3})`.
  - Lower bound, pre-Bedert-2024: the number of zeros tends to infinity (Erdélyi 2016; Sahasrabudhe, *Adv. Math.* 343 (2019), `(log log log n)^{1/2−o(1)}`; Erdélyi, *Acta Arith.* 192 (2020) / arXiv:1702.05823, `(log log log n)^{1−o(1)}`).
  - Current universal lower bound: Bedert, arXiv:2407.16075v2 (7 Jan 2025), published *Israel J. Math.* (30 Nov 2025): `Z(N) ≥ (log log N)^{1−o(1)}`. The precise form is Theorem 1.3,
    `Z(g) ≥ [c / (1+log M(S))] · (log log |g(0)|) / (log log log |g(0)|)`
    with unspecified absolute `c>0`.
- arXiv:2312.04454 (listed in PROBLEM.md) is Bedert's *reciprocal Littlewood* paper (`Z_L(N) → ∞` for `±1` reciprocal polynomials). Related, not the cosine-sum bound Green quotes. Green's [27] is the 2407 paper.
- Isolated root tables are residue. A dent is a certified improvement of either `(log log n)^{1−o(1)}` or `O(n^{2/3} log^{2/3} n)`.

## 2026-08-17 — literature anatomy

### Lower bound (Bedert 2407)

Two pieces:

1. **Structure** (Prop. 4.4, from Erdélyi Lemmas 3.7–3.8 + Sahasrabudhe Lemmas 10–11). If `g` has `d` zeros in `(0,π)` then `[0,N]` splits into
   `K = exp((2M)^{O(d log d)})` intervals on each of which `(a_n)` is periodic of period
   `P = exp(O(d log log d))`.
   Explicitly in Erdélyi: `m = ⌊32 d log log(2d+3)⌋`, `P = d_m := lcm[1..m] < 3^m`, and
   `log q ≤ 60π (8M)^{2d+1} (2d+1)^{d+3/2} L` with `L = (|S|+2)^{4m+2}+6d+3`.

2. **Structured L1** (Prop. 3.1). After multiplying by the nonnegative kernel `(2/P ∑_{0}^{P−1} cos(2π n t))^2`, Littlewood/MPS (Erdélyi Thm 1.7: constant `1/30` on `[0,2π]`) versus an Si / variation upper bound give
   `d · M · P^2 · log(KP) ≫ log |g(0)|`.

Combine: `log N ≪ exp(O(d log d (1+log M)))`, hence `d log d ≫ log log N / (1+log M)`, which is Theorem 1.3.

Bottleneck for a clean `c log log N`: the Hadamard factor `(2d+1)^{d}` inside `log q`. The period `P = exp(O(d log log d))` is milder.

### Construction (JS 2020 / Konyagin 2020)

The BEFL family, sharply analysed:
`f = D_n − g`, `D_n = ∑_{k=0}^n cos(kx)`, `g` a `{0,1}`-cosine polynomial of degree `m`.
Zeros of `f` can only occur on `E(g) = {x ∈ (0,π] : |g(x)−1/2| < s(x)}`, `s(x) = 1/(2 sin(x/2))`.
JS Lemma 3.1 (deterministic): `n|E|/2π − C m ≲ Z(f) ≲ C_α (n|E| + m) + c n^{0.6}` when `deg g ≤ n^{1−α}`.
For *random* `g ∼ Bernoulli(1/2)` on `[0,m]`, `𝔼|E(g)| = Θ(log m / √m)` (Berry–Esseen + envelope). Optimising `m ∼ (n log n)^{2/3}` yields `Θ((n log n)^{2/3})` in expectation. The `Θ` is for this random model; a special `g` with `|E| = o(log m/√m)` would beat the barrier.

Variance identity: `Var(g(x)) = (1/4)∑ cos²(kx) ≤ m/8 + O(1)`. Random `p=1/2` *maximises* anti-concentration among independent inclusions. Beating the log inside this independent model is impossible; a dent needs dependence or a different ambient set than `[0,n] \ [0,m]`.

## 2026-08-17 — false start: Hankel determinants

Erdélyi Lemma 3.5 feeds Hadamard `M^{d-1} d^{d/2}` into `log q`. Consecutive windows of a bounded sequence are Hankel, so a `C^d` Hankel-det bound would replace `d log d` by `d` and give `Z(N) ≥ c log log N`.

`compute/hankel_det.py`: max `|det|` of `n×n` `{0,1}`-Hankel matrices for `n≤7` is `1,1,2,3,5,9,32` — the same sequence as unrestricted `{0,1}` max-dets (OEIS A003432) through `n=7`. Alphabet `{-2,…,2}` hits the Hadamard number exactly at `n=4`. No exponent to harvest. Named obstruction: Hankel does not beat Hadamard on the worst examples.

## 2026-08-17 — false start: better prefixes

`compute/search_prefix.py` estimates `|E(g)|` by FFT on `(0,π]` for `m=32,64,128,256,512`.

| family | typical `E / (log m / √m)` |
|---|---|
| local search from random | `1.13–1.35` |
| random `p=1/2` | `1.5–2.0` |
| quadratic residues | `1.6–2.8` |
| Thue–Morse, Sturmian | `2.5–5` |
| evens / interval / low half | `4–11` (interval has `E≈π`) |

No structured family beat the random Θ-order. Local search shaves a small constant and stays `Θ(log m/√m)`. Isolated root tables / finite-`m` `|E|` numbers are residue, not a dent of `O((n log n)^{2/3})`.

## 2026-08-17 — the usable click

Bedert Theorem 1.3 already *is* `Z ≥ [c/(1+log M)] loglog|g(0)| / logloglog|g(0)|` with `c` unnamed. Erdélyi Lemmas 3.7–3.8 and Theorem 1.7 are fully numerical. Unwinding Bedert §3 with explicit Si / variation constants names `c`.

Algebraic lift of a `{0,1}`-cosine polynomial has coefficients in `{0,1,2}` (Bedert §4 footnote). Conservative inputs: `S={0,1,2}`, `M=2`, `|S|=3`.

Pipeline (`compute/CONSTANTS.md`, replay `compute/run_all.sh`):

- `c_L = 1/(120π)` (Erdélyi `1/30` on `[0,2π]`, plus the cosine-to-exponential `1/2`).
- `m = ⌊32 d log log(2d+3)⌋`, `P < 3^m`.
- `log q ≤ X = 60π · 16^{2d+1} · (2d+1)^{d+3/2} · L`, `L ≤ 2·5^{4m+2}`.
- `ψ(t)=(1/2)cot(t/2)-1/t` is decreasing `(0,π] → [-1/π,0)`, giving Lemma 3.3 with constant `2/n`.
- `‖g̃‖_1 ≤ 48(d+1)(1+log K̃)`, `1+log K̃ ≤ 2X` (`d≥2`, machine-checked through `d=400`).
- `log N ≤ F(d) := 11520 π (d+1) 3^{2m} X`.
- `log F(d) ≤ 200 d log d` for `4 ≤ d ≤ 2000` (max ratio `183.36` at `d=4`).

Hence any `{0,1}`-cosine `N`-sum with at most `d≥4` zeros in `(0,π)` has `log log N ≤ 200 d log d`, so

```
Z(N) ≥ log log N / (200 log log log N)
```

whenever the right-hand side is at least `4`.

## Published record we compare against

- Best published *form*: Bedert v2 / *Israel J. Math.* 2025, `Z(N) ≥ (log log N)^{1-o(1)}`, equivalently Theorem 1.3 with unspecified `c>0`. We do **not** beat the exponent. We name `c = 1/200` in that form for `S={0,1}`.
- Best published *construction*: Juškevičius–Sahasrabudhe / Konyagin, `O((N log N)^{2/3})`. We did not beat it. Prefix search is residue.

The dent is the explicit constant in Bedert's existing bound, independently replayable. It is not a new exponent and not a new construction.

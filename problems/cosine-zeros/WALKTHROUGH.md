# Walkthrough — Naming the constant in Bedert's `(log log N)^{1-o(1)}`

- Problem: `problems/cosine-zeros`
- Quest: SuperGrok 2026-08-17, Green 100 #82
- Model: grok-4.6 `--reasoning-effort xhigh`
- Date: 2026-08-17
- Argument status: explicit majorant of Bedert + Erdélyi, with a replayable arithmetic certificate; two analytic lemmas (cotangent variation, Si grouping) are human-checked
- Problem status: open. We do not determine the order of `Z(N)`. We do not beat `O((N log N)^{2/3})`.

## 0. What was actually missing

The missing ingredient was not a new structure theorem.
Bedert's 2024/25 paper already proves

```
Z(g) ≥ [c / (1 + log M(S))] · (log log |g(0)|) / (log log log |g(0)|)
```

and then writes the weaker advertisement `Z(N) ≥ (log log N)^{1-o(1)}`. The `c` is never evaluated. Every piece of the chain is finite:

- Erdélyi Theorem 1.7 is Littlewood/MPS with constant `1/30` on `[0,2π]`.
- Erdélyi Lemma 3.7 names `m = ⌊32 d log log(2d+3)⌋` and `d_m < 3^m`.
- Erdélyi Lemma 3.8 is a closed expression for `log q`.
- Bedert Proposition 3.1 is an `L¹` sandwich whose `O(1)`s are Si tails, a cotangent function of bounded variation, and `K̃ = O(PK)`.

The degree of freedom was to *name the numbers*, including the algebraic-lift convention `S = {0,1,2}` for a `{0,1}`-cosine polynomial.

## 1. False starts (named obstacles)

- **A better prefix than Bernoulli(`1/2`).** Juškevičius–Sahasrabudhe analyse `f = D_n − g` with `deg g = m`. Zeros live in `E(g) = {|g−1/2| < 1/(2 sin(x/2))}`, and random `g` has `𝔼|E| = Θ(log m / √m)`. A special `g` with `|E| = o(log m/√m)` would give `O(n^{2/3})` or better. FFT estimates for interval, evens, low-half, Thue–Morse, Sturmian, quadratic residues, biased Bernoulli, and a bit-flip local search all stayed `Θ(log m/√m)` (local search ~`1.2×` the random benchmark). The obstruction is structural: independent inclusions maximise `Var(g(x))` at `p=1/2`, and every highly structured `g` we tried was *more* often inside the envelope, not less. Finite-`m` tables are an incomplete search.

- **Hankel instead of Hadamard.** The `d log d` in `log F` comes from `(2d+1)^{d}` in Erdélyi 3.8, which is Hadamard on a window matrix. Consecutive windows are Hankel. Exhaustive max-`|det|` for `{0,1}`-Hankel of size `n≤7` reproduces the unrestricted `{0,1}` sequence `1,1,2,3,5,9,32`. The restriction does not remove the `n^{n/2}`. No `c log log N`.

- **Chasing `1/5` style improvements of `P`.** The period is already `exp(O(d log log d))` via `lcm[1..m]` and Euler's totient; that term is milder than Hadamard for the inversion. Tightening `16 t log log t` to `8 t log log t` with a better `φ` bound changes `C`, not the form.

- **Isolated exact zero counts.** Exact `Z(A)` for a handful of sets is the thing the house forbids as a new bound.

## 2. The useful failure

The prefix search was the useful failure. It showed that the JS random model is not a sloppy choice: on the obvious structured families, `|E|` is *larger* than random (Dirichlet sits inside the envelope identically; lacunary and mechanical words spend more time near `1/2`). Improving the construction-side `O((n log n)^{2/3})` needs a genuinely different ambient set than `[0,n]` minus a degree-`m` prefix, or a dependent `g` whose law is far from Gaussian. That pushed the work onto constant-tracking of the existing lower-bound argument, which is the thing Bedert left uncomputed.

## 3. The click

Read Bedert past Theorem 1.4 to the one-page §5. The combination is

```
log |g(0)| ≪ d M P² log(KP),
P = exp(O(d log log d)),   K = exp((2M)^{O(d log d)}),
```

and the `O`s are the Erdélyi lemmas plus the Si / variation argument of §3. Specialising to `{0,1}`-cosine sums, lifting to coefficients in `{0,1,2}`, and replacing every `≪` by an integer, one gets an explicit elementary `F(d)` with `log N ≤ F(d)`. Inverting `log F(d) ≤ 200 d log d` is then a finite check.

A second click, smaller: the function `ψ(t) = (1/2)cot(t/2) − 1/t` on `(0,π]` is *strictly decreasing* (`sin u < u`), from `0` to `−1/π`. Bedert's Lemma 3.3 is not an appeal to Zygmund's black box — it is integration by parts against a function of total variation `1/π`.

## 4. The argument, in the order it was found

Let `g(t) = ∑_{n=0}^N a_n cos(n t)` with `a_n ∈ {0,1}`, `g(0) = N`, and `d` zeros in `(0,π)`. Write `2g(t) = G(e^{it}) e^{-i N t}`. The coefficients of `G` lie in `{0,1,2}`.

Erdélyi 3.7–3.8, with `M=2`, `|S|=3`, `m = ⌊32 d log log(2d+3)⌋`, produce a period `P = d_m < 3^m` and a bound `log q ≤ X` on the number of nonzero coefficients of `G(z)(z^{d_m}−1)² Q(z)`. The coefficient sequence of `g` therefore splits into `K` intervals, each `P`-periodic, with

```
log K ≤ X + 8 P log 3.
```

(The second term covers short-interval singletons of length at most `|S|^{O(P)}`.)

Rescale to `[0,1]` and multiply by Bedert's nonnegative kernel `φ(t) = (2/P ∑_{0}^{P−1} cos(2π n t))²`. Then `g̃ = g φ` has the same sign changes as `g`, coefficients in `P^{-2}ℤ ∩ [-4,4]` (`check_kernel.py` for `P≤24`; the identities are degree-`2P` trigonometric), and `|g̃(0)| = 4N`. Littlewood/Erdélyi 1.7, converted to `[0,1]` and paying `1/2` for cosine versus exponential coefficients, gives

```
‖g̃‖_1 ≥ log N / (120 π P²).
```

For the matching upper bound: `‖g̃‖_1 ≤ 4(d+1) sup|G|`, `G(x) = ∫_0^x g̃`. Expanding in Dirichlet kernels and using `ψ` as above replaces each block by an Si difference with error `1/(π n_j)`. The Si sum itself is `≤ 12(1+log K̃)` by Bedert's unit-interval grouping and `|∫_y^{y'} sin t/t dt| ≤ (2/y) min(1,|y'−y|)` for `y>1`. Hence `sup|G| ≤ 12(1+log K̃)` and

```
‖g̃‖_1 ≤ 48 (d+1) (1 + log K̃).
```

`K̃ ≤ 5 P K` and the comparison `1+log K̃ ≤ 2X` (`d≥2`, checked through `d=400`) produce the majorant

```
log N ≤ F(d) := 11520 π (d+1) · 3^{2m} · X.
```

`verify_certificate.py` rebuilds `F` from these formulas and checks `log F(d) ≤ 200 d log d` on `4 ≤ d ≤ 2000` (largest ratio `183.36` at `d=4`). Therefore

```
Z(N) ≥ d ≥ log log N / (200 log log log N)
```

whenever the right-hand side is at least `4`.

## 5. Computer search

- `compute/prefix_search.json` — `|E|` table. Best finite-`m` ratio is local search, still `Θ(log m/√m)`.
- `compute/hankel_det.py` stdout — Hankel max-dets.
- `compute/bedert_ratios.json` — `log F(d)/(d log d)` from `d=2` to `1600`.
- `compute/certificate.json` — the `C=200` check.
- `compute/check_si_group.py` — sampled Si sums sit at `≤ 0.06` of the `12(1+log K)` majorant.

None of these tables is a bound.

## 6. What is proved vs still open

Proved tonight: an explicit constant in Bedert's existing theorem, for `{0,1}` coefficients,
`Z(N) ≥ log log N / (200 log log log N)` when the right-hand side is `≥ 4`. Replay: `compute/run_all.sh`.

Still open: the order of `Z(N)`. The gap

```
(log log N)^{1-o(1)}  ≤  Z(N)  ≤  O((N log N)^{2/3})
```

is unchanged as a pair of function classes. We do not claim `c log log N`, we do not claim `o((N log N)^{2/3})`, and we do not claim Littlewood's `N−1`.

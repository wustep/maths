# Walkthrough — An explicit `1/18` in Bedert's `n^{1/7}`

- Problem: `problems/chowla-cosine`
- Quest: SuperGrok 2026-08-17, Green 100 #81
- Model: grok-4.6 `--reasoning-effort max`
- Date: 2026-08-17
- Argument status: finite algebraic certificate plus a human-checked Young/split chain
- Problem status: open. The `√n` conjecture is not proved. We do not beat Bedert's exponent `1/5−o(1)`.

## 0. What was actually missing

The missing ingredient was not a new structural theorem and not an SDP.
Bedert's §7 already proves a fully polynomial bound `K(n) ≫ n^{1/7}`
(no `o(1)`) by combining

- Roth energy ⇒ a popular difference `t` with `|A ∩ (A+t)| ≥ N/(2K)`,
- Ruzsa ⇒ no long AP, so the one-sided piece `B_t` is still `≫ N/K^3`,
- two nonnegative auxiliaries `1+sin(2π t x)` and `1−cos(2π t x+π/4)`,
- a 5-bit window computation (Lemma 7.2) that isolates `B_t` with gap `√2/2`,
- a decomposition `hat{1}_{B_t} = Q1 + Q2` with `||Q1||_1 ≪ K` and `||Q2||_2 ≪ K^2`.

Every implied constant in that chain is finite. The paper never evaluates
it. The degree of freedom was to *name the numbers*: check the 32 windows
exactly, add the Young errors, enclose one quadratic in `Q(√2)`, and
convert back from the symmetric formulation to Chowla's `K(n)`.

## 1. False starts (named obstacles)

- **Chasing the `1/5−o(1)`.** Bedert's headline exponent is better than
  `1/7`, but the `o(1)` is a genuine `(log n)^{4/5}` coming from a
  divisor-box count (Lemma 7.4, `M ≈ (log n)^2`). There is no implicit
  `c>0` with `K(n) ≥ c n^{1/5}` written down, and making the logs
  explicit produces an `n0` so large it is a worse advertisement than
  a clean `n^{1/7}`. The obstruction was the shape of the bound, not
  the algebra.
- **Enumerating small sets.** `K(n)` is an infimum over all
  `n`-element subsets of `ℕ`. Translation and dilation do not bound
  `max A`. A table of minima for a few structured families is residue.
- **A better auxiliary.** The isolation gap is a function of a 5-bit
  window and of two multipliers `1+α sin`, `1−β cos(θ+φ)`. A 2000-point
  float search (`compute/optimize_aux.py`) plus a local refinement left
  Bedert's `(α,β,φ)=(1,1,π/4)` as the minimiser of the implied `Cstar`
  on that family. The obstruction was not the search: the point is
  already locally optimal, so the dent is not a new polynomial.
- **SDP on the dual.** The house rule forbids claiming an SDP number
  without an exact certificate. We did not run one.

## 2. The useful failure

The auxiliary search was the useful failure. It showed that the two
trig polynomials Bedert wrote down are not a sloppy choice: on the
obvious 3-parameter family they already maximise the isolation-gap /
error-term ratio that feeds `Cstar`. Improving `1/18` by replacing
`1+sin` would need a genuinely different window (higher degree, or a
different convolution power), not a better phase. That pushed the
work onto constant-tracking of the existing argument, which is the
thing the paper left uncomputed.

## 3. The click

Read §7 past the sentence “which combines with Proposition 7.3 to show
that `K ≫ n^{1/7}`”. That sentence is already a polynomial bound with
no logs. Proposition 7.3 is a quadratic inequality whose coefficients
are the four numbers in Lemma 7.2 plus `32`, `3` and `14`. Lemma 7.2
is 32 complex numbers in `Q(√2)`. Those 32 numbers can be, and were,
recomputed from the closed formula

```
hat{f}(m) = 2 a_m − i a_{m−t} + i a_{m+t},
rho_m     = hat{f}(m)^2 − ((1+i)/(2√2)) hat{f}(m−t)^2
                          − ((1−i)/(2√2)) hat{f}(m+t)^2
```

on each five-tuple `(a_{m−2t},…,a_{m+2t}) ∈ {0,1}^5`. The table in
the paper is correct. The gap is exactly `√2/2`.

## 4. The argument, in the order it was found

Symmetric setup (Bedert §3). `A = −A ⊂ ℤ\{0}`, `|A|=N`,
`hat{1}_A + K ≥ 0`. Chowla's `K(n)` for a positive `n`-set `B` is
half of this `K` at `N=2n`, because
`hat{1}_{B∪−B}(x) = 2 ∑_{b∈B} cos(2π b x)`.

If `N < 2K^2`, Roth's hypothesis fails and `K > √(N/2)`, so the
positive-integer bound is already `√n/2`. The rest of the argument
is the energy branch `N ≥ 2K^2`.

Roth (Lemma 4.1) plus averaging over `t ∈ A` produces a difference
with `|A_t| ≥ N/(2K)`. Ruzsa's sliding-window lemma bounds the longest
AP in `A` by `L ≤ 8K^2+8`. Bedert's Lemma 5.3 then upgrades `A_t` to
the one-sided piece `B_t = A_t \ (−A_t)`, of size
`|B_t| ≥ N / (16 K (K^2+1))`.

The two auxiliaries produce a real odd/even pair `(φ_t, ψ_t)` with
`|φ_t| ≤ ψ_t + 32 K^2`. Lemma 7.2, now machine-checked, says

- `hat{ψ}(m) ≤ 4 + 1/√2` for every frequency,
- `|hat{φ}(m)| ≤ 4 + 2√2` for every frequency,
- `−Im rho_m ≥ 4+√2` on every `m ∈ B_t`.

Lemma 7.1 writes `hat{1}_{B_t} = Q1 + Q2` with `|Q1| ≤ 3(hat{1}_A+K)`
and `||Q2||_2 ≤ 14 K^2` (Young plus an overflow split; additions in
`compute/CONSTANTS.md` and `compute/lemma71_bounds.py`). Testing
`|φ| ≤ ψ + 32 K^2` against `|Q1|*|Q1|` produces

```
(√2/2) |B|  ≤  (28 (φ_max + ψ_max)) K^2 √|B|  +  (196 (φ_max+ψ_max) + 288) K^4.
```

Set `z = √|B| / K^2`. Then `z^2 ≤ A z + B` with the exact values
`A = 140 + 224√2`, `B = 980 + 1856√2`. The rational enclosure
`7/5 < √2 < 99/70` and a binary-search square root give
`|B_t| ≤ 215816 K^4`.

Packing against `|B_t| ≥ N/(16 K(K^2+1))` yields
`N ≤ 16 · 215816 · (K^7 + K^5)`. On `K ≥ 1` this is
`N ≤ 32 · 215816 · K^7`. On `K < 1` the same packing is
`N ≤ 32 · 215816 · K^5`, hence `N/(32·215816) < 1` and
`K ≥ (N/(32·215816))^{1/5} ≥ (N/(32·215816))^{1/7}`.
So on the whole energy branch,
`K_sym ≥ (N / (32 · 215816))^{1/7}`.

Convert: `K(n) ≥ K_sym(2n)/2 ≥ (2n / C7)^{1/7} / 2` with
`C7 = 32 · 215816`. This equals `n^{1/7} / (2048 · 215816)^{1/7}`.
The integer comparison `2048 · 215816 = 441991168 ≤ 18^7 = 612220032`
gives `K(n) ≥ n^{1/7}/18`. The energy-failure branch
`K(n) ≥ √n/2` is larger than `n^{1/7}/18` for every `n ≥ 1`.

Therefore, for every `n ≥ 1` and every `n`-element set of positive
integers,

```
min_x  ∑_{a ∈ A} cos(a x)   ≤   − n^{1/7} / 18.
```

## 5. Computer residue

Replay: `cd compute && ./run_all.sh` (exit 0).

- `lemma72.json` — exact table check, gap `√2/2`.
- `certificate.json` — `Cstar_int = 215816`, `C7 = 6906112`, `c = 1/18`.
- `verify_certificate.json` — independent rebuild of the same integers.
- `aux_search.json` — float search, no improvement of `Cstar`.

The 32-window dump lives in the `verify_lemma72.py` stdout; every
row is an element of `Q(√2)`.

## 6. What is proved vs still open

**Proved tonight.** The explicit inequality above. The 32-window half
is independently machine-checked. The Young/split constants `3` and
`14` are a finite inequality chain written in `compute/CONSTANTS.md`.

**Not proved.** Chowla's `√n` conjecture. Any bound of the shape
`K(n) ≥ c n^{1/5}`. Any improvement of Bedert's exponent. An explicit
`c` in Ruzsa's `exp(c √log n)`. Ruzsa's problem on coefficients in
`[0.99, 1.01]`.

**What we did not beat.** Bedert v3's exponent `1/5−o(1)` is stronger
than `1/7` for large `n`. The dent is the *constant*, against a
published record that has no numerical `c` in any polynomial bound.

**Soft spot, stated plainly.** A referee can reject `C_Q1 = 3` or
`C_Q2 = 14` by finding a missing term in the Young/split bookkeeping.
If that happens the 32-window certificate still stands, and the same
pipeline produces some (worse) explicit `c` from whatever pair
`(C_Q1, C_Q2)` survives. The integer comparison `2048 Cstar ≤ 18^7`
has slack (`441991168` vs `612220032`), so a modest inflation of
`Cstar` still gives `1/18`.

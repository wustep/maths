# Attack log — Chowla's cosine problem

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House rules: write only here; no git; cite what we beat.
- Green 100 #81 (Dec 2025 update of `open-problems.pdf`, Harmonic analysis, p. 38): for `|A|=n`, is there `θ` with `∑_{a∈A} cos(aθ) ≤ −c √n`? Construction-sharp upper barrier `K(n) ≪ √n`. Pre-2025 record Ruzsa: `K(n) ≥ exp(c √log n)`. Update 2025 records Bedert and Jin–Milojević–Tomon–Zhang polynomial bounds; Green quotes Bedert as any exponent `< 1/7`.
- Current arXiv (fetched tonight):
  - Bedert, [arXiv:2509.05260v3](https://arxiv.org/abs/2509.05260) (24 Jul 2026): `K(n) ≫ n^{1/5−o(1)}`. Streamlined §5 gives `K(n) ≫ n^{1/12}`. Mid-argument in §7 gives `K(n) ≫ n^{1/7}` with no `o(1)`, then Lemma 7.4 upgrades the `|B_t|` lower bound and produces the `1/5−o(1)`. No numerical `c`.
  - Jin–Milojević–Tomon–Zhang, [arXiv:2509.03490v2](https://arxiv.org/abs/2509.03490): `min ∑ cos(ax) ≤ −|A|^{1/10−o(1)}`.
- Neither paper, nor Green, nor Open Problem Garden, states an explicit numerical `c>0` with `K(n) ≥ c n^α` for a fixed `α`. An SDP float is not a dent. The square-root conjecture is not claimed.

## 2026-08-17 — first false start: extract `c` from `n^{1/5−o(1)}`

- The `o(1)` in Bedert Theorem 1.1 is a real `(log n)^{4/5}` loss (Lemma 7.4, `M ≈ (log n)^2`, `π(M) ≈ M/log M`). An explicit `c` for `n^{1/5}` does not fall out. A bound `K(n) ≥ c n^{1/5}/(log n)^{4/5}` is possible for large `n` but the `n0` where it beats `n^{1/7}` depends on a large `Cstar` and is not the clean dent.
- Abandoned as the main claim. Kept `n^{1/7}` (no logs) as the target.

## 2026-08-17 — second false start: enumerate small `A`

- Exact `K(n)` for small `n` would give a table, not a universal constant. Affine symmetry does not bound `max A`. Residue, not a dent. Not run as a claim.

## 2026-08-17 — third false start: replace `1+sin` by a better auxiliary

- Bedert §7 uses two nonnegative auxiliaries: `1+sin(2π t x)` and `1−cos(2π t x + π/4)`. The isolation gap after multiplying is `√2/2`, coming from a 5-bit window (32 configurations).
- Searched `(α, β, φ)` for `f = 2(1+α sin) hat{1}_A` and `r = (1−β cos(θ+φ))(f*f)` on a `11 × 11 × 17` grid plus a local refinement (`optimize_aux.py`). Bedert's `(1, 1, π/4)` already minimises the implied `Cstar` on that family. No new auxiliary.

## 2026-08-17 — the click

- Section 7 of Bedert already proves `|B_t| ≪ K^4` by testing `|φ_t| ≤ ψ_t + 32 K^2` against `|Q1|*|Q1|`. Combined with Roth+AP `|B_t| ≫ N/K^3` this is `K ≫ N^{1/7}` with **no `o(1)`**. The implied constant is uncomputed in the paper but every piece is finite:
  1. Lemma 7.2 is 32 exact algebraic numbers.
  2. Lemma 7.1 is Young + an overflow split; the additions give `|Q1| ≤ 3(hat{1}_A+K)` and `||Q2||_2 ≤ 14 K^2`.
  3. The quadratic `z^2 ≤ A z + B` with `A, B ∈ Q(√2)` has a rational enclosure.

## 2026-08-17 — certificate

- `verify_lemma72.py`: all 32 windows match Bedert's table exactly in `Q(√2)`. Gap `√2/2`.
- `track_constants.py` / `verify_certificate.py`: `Cstar ≤ 215816`, `2048 · 215816 = 441991168 ≤ 18^7 = 612220032`.
- Conversion through the symmetric formulation (`hat{1}_{B∪−B} = 2 ∑ cos(2π b x)`) yields, for every `n ≥ 1`,

  `K(n) ≥ n^{1/7} / 18`.

- Replay: `compute/run_all.sh` (exit 0).
- What this does **not** do: beat Bedert's exponent `1/5−o(1)`; prove the `√n` conjecture; produce an SDP dual without a sum-of-squares certificate.

## Published record we compare against

- Best published *exponent*: Bedert v3, `n^{1/5−o(1)}`. We do not beat the exponent.
- Best published *explicit numerical* `c` in a bound `K(n) ≥ c n^α` (`α > 0` fixed): none found in Green #81, Bedert v3, JMTZ v2, Ruzsa 2004, Open Problem Garden, or the May 2026 conjugate-function paper arXiv:2605.18087 (which cites `1/7−o(1)` / `1/10−o(1)` and does not give a numerical `c`).
- Best published explicit-form weaker bound: Littlewood/`L^1` ⇒ `K(n) ≫ log n` (McGehee–Pigno–Smith / Konyagin). Steen–Cambridge notes record that `A = 128` works in the `L^1` inequality; that is a logarithmic bound, beaten by `n^{1/7}/18` for all large `n`.

The dent is the constant `1/18` in a fully polynomial bound, independently replayable, not a new exponent.

# Constants used in the n^{1/7}/18 bound

Replay: `./run_all.sh` (exit 0).

## Machine-checked

- Bedert Lemma 7.2, all 32 five-bit windows, exact in `Q(sqrt(2))`: `verify_lemma72.py`.
  Isolation gap `min_{B_t}(-Im rho) - max Re rho = sqrt(2)/2`.
- Rational enclosure `7/5 < sqrt(2) < 99/70` (because `49 < 50` and `9801 > 9800`).
- Quadratic `z^2 <= A z + B` with `A = 140 + 224 sqrt(2)`, `B = 980 + 1856 sqrt(2)`,
  then `Cstar <= 215816` and `2048 * 215816 = 441991168 <= 18^7 = 612220032`.
  Scripts: `track_constants.py`, `verify_certificate.py`.

## Human-checked inequality chain (arithmetic packed in `lemma71_bounds.py`)

Notation as in Bedert §3–§7. Symmetric `A = -A subset Z\{0}`, `|A| = N`,
`hat{1}_A + K >= 0`. Auxiliary:

- `f_t = 2 (1 + sin(2 pi t x)) hat{1}_A`, so `||f_t||_min <= 4K`.
- `f_t * f_t >= -16 K^2`.
- `r_t = (1 - cos(2 pi t x + pi/4)) (f_t * f_t)`, so `r_t >= -32 K^2`.
- `phi_t`, `psi_t` even/odd parts: `|phi| <= psi + 32 K^2`.

Lemma 7.1 split of `hat{1}_{B_t} = Q1 + Q2`, for `K >= 0`:

- `hat{1}_A = T1 + T2` with `T1 = max(hat{1}_A, 0)`, `T2 = min(hat{1}_A, 0)`,
  `||T1||_1 <= K`, `||T2||_inf <= K`, `||T2||_1 <= K`, `|T1| <= hat{1}_A + K`.
- Convolution identity `(hat{1}_A + K)*(hat{1}_A + K) = hat{1}_A + K^2`.
- Young: `||u * v||_inf <= ||u||_1 ||v||_inf`.
- Overflow split: if `|S| <= hat{1}_A + K^2`, write `S = U + V` with
  `|U| <= hat{1}_A + K` and `||V||_inf <= max(K^2 - K, 0) <= K^2`.
- Collecting the even piece: `|R1| <= 4(hat{1}_A + K)`, `||R2||_2 <= 20 K^2 - 6K`.
- Odd piece: `|S1| <= 2(hat{1}_A + K)`, `||S2||_2 <= 8 K^2 - 2K`.
- `Q1 = R1/2 + S1/2`, so `|Q1| <= 3(hat{1}_A + K)`, `||Q1||_1 <= 3K`.
- `Q2 = R2/2 + S2/2`, so `||Q2||_2 <= 14 K^2 - 4K <= 14 K^2`.
- Hermitian average `Q_j(x) |-> (Q_j(x) + conj(Q_j(-x)))/2` preserves both
  bounds because `hat{1}_A` is even.

Proposition 7.3 test against `H * H`, `H = |Q1|`, then produces
`|B_t| <= Cstar K^4` with `Cstar <= 215816`.

Roth + AP:

- If `N < 2 K^2` then `K > sqrt(N/2)`.
- If `N >= 2 K^2` some `t in A` has `|A_t| >= N/(2K)` (Roth, Lemma 4.1).
- Longest AP in `A` has length `L <= 8 K^2 + 8` (Ruzsa / Bedert Lemma 4.2–4.4
  for `L >= 9`; for `L <= 8` the bound is immediate).
- Lemma 5.3: `|B_t| >= |A_t| / L >= N / (16 K (K^2 + 1))`.

Packing: `N <= 16 Cstar (K^7 + K^5)`. Hence

- if `K >= 1`, `N <= 32 Cstar K^7`;
- if `K < 1`, `N <= 32 Cstar K^5`, so `N / (32 Cstar) < 1` and
  `K >= (N/(32 Cstar))^{1/5} >= (N/(32 Cstar))^{1/7}`.

In all energy-branch cases `K >= (N / (32 Cstar))^{1/7}`.

Positive-integer form: `A = B union -B`, `|B| = n`, `N = 2n`,
`hat{1}_A(x) = 2 sum_{b in B} cos(2 pi b x)`, so Chowla `K(n) >= K_sym(2n)/2`.
The energy-failure branch is `K(n) >= sqrt(n)/2`. Both branches are at least
`n^{1/7}/18` because `2048 * 215816 <= 18^7` and `sqrt(n)/2 >= n^{1/7}/18`
for every `n >= 1`.

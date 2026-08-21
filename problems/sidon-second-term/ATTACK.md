# Attack log — second term for Sidon subsets of [N]

## 2026-08-17 — literature (do not claim Erdős–Turán)

Fetched:

- Green, *100 Open Problems* (update Dec 2025), Problem 31: improve, for infinitely
  many $N$, the bounds $N^{1/2}+O(1)\le F(N)\le N^{1/2}+N^{1/4}+O(1)$. Comments
  record Balogh–Füredi–Roy $0.998$ (2021) and Carter–Hunter–O’Bryant $0.98183$
  (2023/2025).
- Erdős Problems #30, accessed 2026-08-17 (page last edited 2026-04-06): still
  **OPEN**. The page states the $ \$1000 $ form $h(N)=N^{1/2}+O_\varepsilon(N^\varepsilon)$
  and records the published upper bound
  $h(N)\le N^{1/2}+0.98183\,N^{1/4}+O(1)$ of Carter–Hunter–O’Bryant,
  Acta Math. Hungar. 175 (2025), 108–126 (arXiv:2310.20032). Singer gives the
  matching-order lower bound. Zero claimed proofs. Forum notes an unpublished
  AlphaEvolve refinement $0.97633$ (Tao, 17 Feb 2026) and a tentative further
  argument “subject to confirmation”.
- Tao–Davis et al. optimization-constants page $C_{5a}$: published upper bounds
  stop at CHO25 $0.98183$; $0.97633$ is listed as unpublished.
- Hou–Zhao, arXiv:2607.01169v2 (5 Jul 2026), *Vector-valued smoothing for finite
  Sidon sets*: claim
  $F(N)\le N^{1/2}+0.9435\,N^{1/4}+O(1)$
  via an eight-kernel rational certificate. Ancillary code:
  https://github.com/HbZhao1/sidon-vector-smoothing.
  This is **later than** the Erdős #30 page edit and **later than** the
  PROBLEM.md “best general upper bound” line. It is the current arXiv record.

Published record I must beat, after the fetch: **Hou–Zhao $0.9435$**, not
CHO25 $0.98183$. Reproducing anything in $(0.9435,0.98183]$ is verification
of a weaker constant, not a dent. Isolated small-$N$ Sidon tables are residue.

Do not claim the Erdős–Turán conjecture.

## 2026-08-17 — tonight’s handle

Three live handles, in order of plausibility:

1. Re-optimize the Hou–Zhao vector-smoothing program (more kernels, finer grid,
   longer boundary, or a lemma that drops kernel symmetry) and emit an
   independent rational certificate with $\sqrt{ab}<0.9435$.
2. Independently verify Hou–Zhao’s eight-kernel certificate (so the residue is
   not “we trusted a PDF”).
3. Lower bound: Singer / Bose–Chowla give $F(N)\ge\sqrt{N}+O(1)$ infinitely
  often (second term $\to 1/2$ along Singer moduli). A growing second term
  needs either $\omega(1)$ extra integer points on an infinite family, or an
  unwrap with a gap $\omega(\sqrt{q})$. Green #32 only guarantees a gap
  $2\sqrt{p}$ (Shakan), which still produces only $O(1)$ after unwrap.
  Adding a bounded number of points to Singer is still $O(1)$. This is the
  historically hard side.

Starting with (2) then (1).

## 2026-08-17 — Hou–Zhao certificate, independent check

Downloaded `HbZhao1/sidon-vector-smoothing` into `compute/refs/`.
SHA-256 of `sidon_certificate_8kernel.py` is
`957a5afadd849ac4f97c2b71252abb5c796c2db3c91a608ab35097e3c49292a8`,
matching the hash printed in arXiv:2607.01169v2 Claim 4.1.

`compute/verify_houzhao.py` re-reads only the integer tables, rebuilds
λ, p, w from the paper’s denominators / η-shift, and checks Lemma 2.1
with `fractions.Fraction`. Result:

- all 129 covering inequalities hold (min slack = 0 at q = 128)
- least positive slack = 4735171805469436153 / 6250000000000000000000000000000
- a, b match the fractions in Claim 4.1
- √(ab) = 0.943492590713545 < 0.9435

So Hou–Zhao is a real published bound, not a blog claim. The constant to
beat is 0.9435. Their two-kernel file `sidon_certificate.py` only claims
C < 0.94601; not needed once the eight-kernel check passed.

Next: independent QP + search (symmetric 1-kernel grid, asymmetric
1-kernel, R=2, R=9 continuation). A floating γ is not a dent.

## 2026-08-17 — Table 1 replay

`search_kernels.py --phase replay` re-solves the fixed-kernel QP with our
own NNLS dual. The eight floating Table 1 values match Hou–Zhao to all
printed digits (R=1: 0.9461473014, …, R=8: 0.94349259006). So the
independent solver agrees with theirs.

## 2026-08-17 — false starts

- **1-kernel (m,L) grid.** Best floats sit around 0.9462–0.9468, matching
  Hou–Zhao’s R=1 row. No path to 0.9435 with one kernel.
- **m-refinement of the published histograms** (repeat each bin). `a` is
  invariant and `b` does not move. Shape, not grid, is the bottleneck.
- **Bose–Chowla + greedy extras** (`construct_bose.py`). Construction
  checks Sidon for every prime 3≤p≤79. Extra points inside [p²-1]: 1,1
  then **0 for all p≥7**. Wide-interval extras are +1 and make the
  second term vs √N worse. Bounded extras are still O(1).
- **Singer + greedy extras** (`construct_singer.py`). All 11 primes
  p≤31 give a Sidon set of size p+1 in [p²+p+1], second term → ½, and
  **zero extras** in the interval. Expected: a Singer unfolding already
  uses every difference in range.
- **CHO two-window replay** (`cho_two_windows.py`). Published parameters
  give b_∞ ≤ 1.990578 on a 400² grid, i.e. C ≤ 0.99529, weaker than
  Hou–Zhao. Not a dent.

## 2026-08-17 — the L-lift

Hou–Zhao Lemma 2.1 treats L as a free parameter. Their certificate uses
L=4. The same (λ,p) with w padded by ones is feasible for every L'>4,
so the L' quadratic program can only decrease b. Independent QP:

| L | floating √(ab) |
| --- | --- |
| 4 | 0.943492590061 |
| 5 | 0.943492509730 |
| 6 | 0.943492508484 |
| ≥8 | 0.943492508467 |

Saturates at L=6. a is exactly the Claim 4.1 fraction (kernels
unchanged). `certify_l6.py` re-solves L=6, rounds w at 10^{-12}, adds a
common η, and writes `certs/hz_kernels_L6.json`.

Exact check (`verify_certificate.py`, then `verify_beat_hz.py` which
does not import the other verifier):

- all 193 covering inequalities hold (min slack 0)
- a equals Hou–Zhao Claim 4.1
- √(ab) = 0.9434925085033526 < γ0 = 0.943492590713545
- ab < (0.94349251)²

So

    F(N) ≤ √N + 0.94349251 N^{1/4} + O(1)

holds for all large N. This is a strict improvement of Hou–Zhao’s exact
certificate constant by 8.22×10^{-8}. It is **not** a new method, and it
does not improve their four-decimal statement 0.9435 (they already had
γ0 < 0.9435). It does improve the PROBLEM.md target 0.98183, but that
target was already superseded on arXiv in July 2026.

## 2026-08-17 — leftover searches killed

Multi-scale sanity recovered the equal-m Hou–Zhao value exactly, so the
different-width lemma specialises correctly. The outer Powell search
(two widths, then HZ+new scale) and the eight-kernel coordinate descent
produced no evaluation below the L=6 plateau in ~9 minutes (one QP
evaluation of R=8, L=6 is already expensive; Powell never returned).
Killed. grid1 died earlier on an infeasible covering row from a
degenerate seed.

No search found a constant at the 0.9434 level. The only certified
improvement of Hou–Zhao’s γ0 is the L=6 lift.

Replay:

```bash
python3 compute/verify_houzhao.py
python3 compute/verify_certificate.py compute/certs/hz_kernels_L6.json --beat 0.94349259
python3 compute/verify_beat_hz.py
```

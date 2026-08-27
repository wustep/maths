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

## 2026-08-27 — q1, continue the vector-smoothing search

Published record is still Hou–Zhao arXiv:2607.01169v2: $F(N)\le N^{1/2}+0.9435\,N^{1/4}+O(1)$.
Fetched the abs page and the HTML. Still v2 (5 Jul 2026); no v3. Green #31
(Dec 2025 PDF) still cites CHO $0.98183$. Tao $C_{5a}$ still stops at CHO /
unpublished $0.97633$ and does not list Hou–Zhao. Erdős #30 was behind
Cloudflare this session.

The 2026-08-17 L=6 lift already has $\sqrt{ab}=0.9434925085<\gamma_0$, but
it does not change the four-decimal statement $0.9435$. Hou–Zhao §5 asks
for a systematic outer search and more kernels. q1 takes the leftover
handles with L-BFGS instead of Powell:

1. joint free-histogram re-opt of all eight published kernels at $L=6$
2. continuation $R=9,10,12$ with 12 cosine modes at $L=6$
3. drop kernel symmetry (independent left/right weights)
4. resample to $m=48$ and re-shape (not a bin-split)
5. two-width L-BFGS

A floating $\gamma$ is not a dent. Code: `compute/q1/`.

Independent replay this session (exact, then floating QP):

- `verify_houzhao.py` PASS. Hash matches Claim 4.1. All 129 covering
  inequalities hold. $\sqrt{ab}=0.943492590713545<0.9435$.
- q1 floating Table 1 matches Hou–Zhao to all printed digits
  (R=1: $0.9461473014$, …, R=8 L=4: $0.94349259006$).
- Same kernels at L=6: $0.94349250848$. Independent left/right weights
  on the symmetric mix give the same number, as they should.

## 2026-08-27 — q1 dent: free histograms beat 0.9435

L-BFGS on the eight published kernels, now as free symmetric
histograms (16 half-logits each) at $L=6$, dropped the floating
$\gamma$ from the L=6 plateau $0.9434925085$ to $0.9432425303$
(maxiter 40, not declared converged). Adding $R=9,\ldots,12$
twelve-mode kernels from the *published* mix only reached $0.94326$,
so the leftover slack was in the six-mode shape class, not in $R$.

`rationalize_certificate.py` on `candidates/joint-lbfgs-hz8-L6.json`
wrote `compute/q1/certs/joint_r8_L6.json`. Exact check:

- all 193 covering inequalities hold (min slack 0)
- $\sqrt{ab}=0.9432425309706136$
- $ab<(0.943243)^2<(0.94325)^2<(0.9433)^2<(0.9435)^2$

Three verifiers that do not share covering code all PASS:

```bash
python3 compute/verify_certificate.py compute/q1/certs/joint_r8_L6.json --beat 0.94325
python3 compute/q1/verify_q1.py compute/q1/certs/joint_r8_L6.json --beat 0.94325
# gcc -O2 -o compute/q1/verify_q1 compute/q1/verify_q1.c -lgmp
# python3 compute/q1/dump_cert.py ... && ./compute/q1/verify_q1 ... 94325 100000
```

So

    F(N) ≤ √N + 0.94325 N^{1/4} + O(1)

holds for all large $N$. This is a dent of Hou–Zhao’s published
four-decimal statement $0.9435$, not only of their $\gamma_0$. Same
lemma, new kernels. SHA-256 of the JSON:
`edcc2c973809c4bb8a3f25233ffc80e6b5ce432a70c4d01697a3ba8ead8beda5`.

Adding $R=9$–$12$ twelve-mode kernels on the published mix reached
$0.94326$, worse than the free-histogram $R=8$. A longer L-BFGS refine
of the certified mix, the dropped-symmetry search, the $m=48$ reshape,
and the two-width L-BFGS had not returned a stricter rational when
this was written. Those leftover phases are residue, not a bound.

## 2026-08-27 — q2, leftover check and a different route

Published record is still Hou–Zhao arXiv:2607.01169v2 (opened abs and
HTML this session; still v2, 5 Jul 2026, no v3). Green #31 (Dec 2025
PDF) still cites CHO $0.98183$. Tao $C_{5a}$ still stops at CHO /
unpublished $0.97633$ and does not list Hou–Zhao. Erdős #30 was behind
Cloudflare again.

Independent replay of the folder record this session:

```bash
cd compute/q1 && ./run_all.sh
```

Python nested-loop and convolution verifiers both PASS on
`q1/certs/joint_r8_L6.json` with $\sqrt{ab}=0.9432425309706136$. SHA-256
still `edcc2c973809c4bb8a3f25233ffc80e6b5ce432a70c4d01697a3ba8ead8beda5`.
The GMP C check needed `libgmp-dev` in this environment; after that
install it also PASS (`ab < (0.94325)^2`). Do not regress this
certificate.

q1 `search.jsonl` has `nosym-start` and `refine-start` and no finished
`nosym-lbfgs-L6` / `nosym-meta` / `refine-lbfgs` row. No `finer` or
`widths` rows at all. Replay: `python3 compute/q2/leftover_check.py`.
Those two phases are residue. q2 does not continue them.

Hou–Zhao Lemma 2.1 still requires symmetric kernels; §5 asks for more
kernels / a systematic outer search, and mentions cross-kernel
correlations with a positivity constraint (not implemented here).
Route in `compute/q2/`:

1. L-lift of the *q1* kernels (L is free; q1 only certified L=6)
2. block coordinate descent, one mix or one histogram at a time
3. grow R by adding *free* histograms to the q1 mix, not 12-mode
   cosine profiles on the published mix
4. resample that mix to $m=48$ and re-block

A floating γ is not a dent.

## 2026-08-27 — q2 L-lift of the q1 kernels

Independent QP on the stored q1 float mix:

| L | floating √(ab) |
| --- | --- |
| 6 | 0.9432425303235829 |
| 7 | 0.9432425303106731 |
| 8 | 0.9432425303103693 |
| 10 | 0.943242530310367 |

Saturates by L=8. The drop from L=6 is $1.3\times 10^{-11}$, smaller
than the rationalization gap on the existing certificate. Same shape
class; more boundary is not a new four-decimal statement. Kept as a
log, not a new cert.

## 2026-08-27 — q2 dent: m=48 free histograms, C<0.94301

Block coordinate descent on the q1 mix (one mix or one histogram at a
time, four cycles) reached floating $\gamma=0.94324234566$. Adding
free-histogram kernels $R=9,10,11$ to that mix only saved another
$2\times 10^{-8}$. The leftover slack was not a ninth six-mode profile
and not more $R$ on the 32-bin grid.

Piecewise-constant resample of the $R=11$ mix to $m=48$ first jumped
*up* to $0.943709$ (the 32-bin shapes are not already continuous-limit
optimal on the finer grid). Two block cycles on that 48-bin mix dropped
the float to $0.94300616604$.

`rationalize_certificate.py` on `candidates/resample-m48-best.json`
wrote `compute/q2/certs/r11_m48_L6.json`. Exact check:

- all 289 covering inequalities hold (min slack 0)
- $\sqrt{ab}=0.943006169985179$
- $ab<(0.94301)^2<(0.94325)^2<(0.9435)^2$

Three verifiers that do not share covering code all PASS:

```bash
cd compute/q2 && ./run_all.sh
```

that is: leftover check, q1 cert still beats $0.94325$, then

```bash
python3 compute/verify_certificate.py compute/q2/certs/r11_m48_L6.json --beat 0.94301
python3 compute/q2/verify_q2.py compute/q2/certs/r11_m48_L6.json --beat 0.94301
# gcc -O2 -o compute/q2/verify_q2 compute/q2/verify_q2.c -lgmp
# python3 compute/q2/dump_cert.py ... && ./compute/q2/verify_q2 ... 94301 100000
```

So

    F(N) ≤ √N + 0.94301 N^{1/4} + O(1)

holds for all large $N$. This is a dent of the folder record $0.94325$
and of Hou–Zhao’s published $0.9435$. Same lemma, finer free histograms.
SHA-256 of the JSON:
`341cba5bd8364cd315561d1b89ad3e3ba0c9d5160047781d86c40213b53b02c6`.

Erdős–Turán not claimed. No growing lower-bound second term.

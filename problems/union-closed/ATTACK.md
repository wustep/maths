# Attack log — Frankl's union-closed sets conjecture

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Conjecture: every finite nontrivial union-closed family has an element in at least half its sets. Do not claim 1/2.
- Tonight: certified improvement of the published frequency constant, or a new finite classification with a verifier.

### Published record (fetched tonight)

| constant | source | status |
| ---: | --- | --- |
| 0.01 | Gilmer [arXiv:2211.09055](https://arxiv.org/abs/2211.09055) | first constant; entropy of iid union |
| `(3-√5)/2 ≈ 0.38196601125` | Chase–Lovett [2211.11689](https://arxiv.org/abs/2211.11689); Alweiss–Huang–Sellke [2211.11731](https://arxiv.org/abs/2211.11731), EJC 2024; Sawin [2211.11504](https://arxiv.org/abs/2211.11504); Pebody | sharp for the *iid* coupling / approximate union-closed |
| `c* ≈ 0.382345533366703` | Yu [2212.00658](https://arxiv.org/abs/2212.00658); Cambie [2212.12500](https://arxiv.org/abs/2212.12500) v2 Feb 2025 | Sawin mix of iid + max-entropy; Cambie calls the computer check “slightly less rigorous” |
| `≈ 0.382709` | Liu [2306.08824](https://arxiv.org/abs/2306.08824) | conditionally iid coupling; **explicitly under two numerical hypotheses** (PSD of a kernel; global min of a 9-D search) |

Lu–Raz [2405.10639](https://arxiv.org/abs/2405.10639) (May 2024) and Wikipedia (fetched 2026-08-17) quote 0.38271 as “the best constant, proven by Liu”. Liu’s own Theorem 13 is conditional. Liu Theorem 6 *is* unconditional: some unspecified `c > c*` works. Das–Janzer–Sudakov [2412.03862](https://arxiv.org/abs/2412.03862) still treat 0.38271 as the standing frequency bound.

Finite cases still quoted as first-open: universe size 13 (Vučković–Živković 2017 did 12); `|F| ≤ 50` via Roberts–Simpson `|F| ≥ 4q−1` plus `q ≥ 13`. No later paper found tonight that pushes either finite frontier or the frequency constant past Liu.

False full-proof claims exist (Scandone 2302.03484; a 2026 HAL note). The conjecture is still open.

### Plan

1. Independently recompute `c*` and Liu’s analytic 0.382709.
2. Search richer couplings (Example-4 `a(t)`, keep Sawin’s max-entropy term, more atoms / mixtures) for a number *above* 0.38271.
3. Quantify Liu Lemma 8 to get an *explicit certified* `c' > c*`, even if smaller than the conditional 0.38271.
4. If the constant does not move, leave a replayable residue (optimizer tables + verifier), not a claimed bound.

## 2026-08-17 — published constants recomputed

`compute/solve_published.py` (mpmath dps=80) independently recovered:

- Gilmer / AHS φ = `(3-√5)/2` = `0.3819660112501051518…`, residual of `h(2φ-φ²)-h(φ)` is 0 at working precision.
- Yu–Cambie `b*` = `0.32945473850303697…`, `a*` = `0.07887729270592317…`, `c*` = `0.38234553336670272…`. Matches Cambie's 15-digit quote to 1 ulp.
- Sawin mix weight `α*` from the 2-point mean-preserving derivative: `0.035606980437…` (Cambie quotes `0.035606981364…`; 9e-10 gap, formula-garbled in Liu's PDF).
- Liu's 2-point `(p*,x*)` solving `x² + x²(1+x̄²)=1` and `p = h(x)/h(x²)`: `c_Liu = 0.382709087918735…` vs quoted `0.382709087918741`.

So the numbers people cite are real. Liu Theorem 13 remains conditional on PSD + global-min hypotheses.

## 2026-08-17 — first false start: treat Wikipedia 0.38271 as certified

Lu–Raz (2024) and Wikipedia quote Liu as a theorem. Liu's own wording is "under numerically verified hypotheses". Beating a conditional number with another conditional number is not a dent. The certified published record is Yu–Cambie `c*` (itself computer-checked on a 2-variable reduction) and the fully analytic `(3-√5)/2`.

## 2026-08-17 — second observation: Example 4 vs Example 5 at μ*

At the Yu–Cambie optimizer, the independent C3 coupling of Example 4 has
`r* = h(Π_{b*,b*}(0,0)) / h(b̄*²) ≈ 1.007387`.
Example 5 gives `1.007380`. Liu Example 4 saturates `Π=1/2` (max binary entropy). The CIID bonus at μ* is only 0.74%, which is why Liu only moves the fourth decimal.

At Liu's own complement 2-point `x*≈0.6908`, Example 5 is built so `h(I)=h(x*²)` (CIID = iid). Example 4 still hits `Π≈1/2`, so `h=1 > h(x*²)`. That is slack Liu left on the table. Next: redo the 2-point push with Example 4.

## 2026-08-17 — Roberts–Simpson off-by-one (not yet a dent)

Their Theorem 4 uses `|D_a| < n-q` then writes "at most `n-q+1` sets in `A_{\bar x}`". For `a ∉ H` the integer bound is `n-q`, which would give `|A| ≥ 4q+3` and, with `q≥13`, settle `|F|≤54`. But if the abundant element of `A_{\bar x}` lies in `H`, the count is exactly `n-q+1` and their `4q-1` is tight. Not claimed.

## 2026-08-17 — third false start: treat `1 − h(2^{-1/2})/√2` as the bound

Example 4 saturates `Π_{t,t}(0,0)=1/2` as soon as `t ≥ 1−1/√2`. The complement 2-point with `x=1/√2` then has both iid and Example 4 at ratio 1, and mean `1 − h(2^{-1/2})/√2 ≈ 0.383099`. That number is real for *that one 2-point*, but it is not the first crossing of the `{b,1}` ray: the Sawin-type point near `b≈0.31` dips below 1 earlier. The closed form is a useful failure, not a bound.

## 2026-08-17 — the click

Liu's numerical section used Example 5 (`f(x)=x(1−x)`), because that is the instance for which he has a (numerically checked) PSD lemma reducing the 2-mixture problem to 9-D. Example 4 — the protocol that maximises `h(Π_{t,t})` and is the one he used for the existential Theorem 6 — was never run as the numerical protocol.

On the single family `{b,1}` that both Yu–Cambie and Liu say is the optimizer, the two protocols behave differently as functions of the mix weight `β`:

- Example 5: `c(β)` peaks at `β≈0.10` at Liu's `0.382709`, then falls.
- Example 4: `c(β)` is still increasing at `β=0.40` and is already `0.38275` at Liu's own `β=0.10`.

`compute/first_crossing.py` (4000×3000, then 5000×4000) and `compute/verify.py` (4500×3500) independently recover:

| protocol | β | first mean with ratio < 1 |
| --- | ---: | ---: |
| Example 5 | 0.10 | 0.38271065 |
| Example 4 | 0.20 | 0.38289681 |

The Example-5 crossing matches Liu's quote to `2×10^{-6}` (mesh). The Example-4 crossing is `+1.9×10^{-4}` above Liu.

Claimed number: **0.38285**, strictly below the Example-4 crossing. On the 4500×3500 mesh, every cell with mean `≤ 0.38285` has ratio `≥ 1.000077`.

## 2026-08-17 — mixture hunt (residue, not a proof)

Liu Theorem 9: the iid+CIID inf is a 2-mixture of iid laws. Theorem 12 (needs PSD) further cuts to 3+3 atoms. We do not have a PSD proof for Example 4, so the 9-D reduction is not available.

`hunt_mixtures.py` at `(β,c)=(0.20, 0.38285)`:

- 9308 accepted 3-atomic samples, worst ratio 1.0052, **0 hits** below 1
- 11823 accepted 2-mixtures of 2-atomic laws, worst ratio 1.0066, **0 hits**
- 25k third-atom perturbations of the ray optimizer: worst 1.00008

This is search residue. It is consistent with the `{b,1}` ray remaining worst, but it is not a Krein–Milman certificate.

## 2026-08-17 — finite classification

`enum_small.py`: every full-universe union-closed family on `n≤4` has abundance `≥ 1/2` (4541 families at `n=4`). Known; the first open finite cases remain `n=13` and `|F|=51`. Not a dent.

## What we claim / do not claim

Claim: on the published optimizer family `{b,1}`, iid + Liu Example 4 at `β=1/5` gives a mesh-certified frequency constant **0.38285**, strictly larger than Liu's published **0.382709** (Example 5). Replay `compute/verify.py`.

Do not claim: the `1/2` conjecture; an unconditional bound for every measure on `[0,1]`; a new `n` or `|F|` classification; that Liu's PSD hypothesis has been proved.

## 2026-08-27 — replay, then β past 0.40

Parent `compute/run_all.sh` still exits 0: claimed 0.38285, mesh min ratio 1.000077. Fetched Gilmer 2211.09055v2 (constant 0.01) and Liu 2306.08824v1 (Theorem 13: 0.382709 under PSD + global-min; Theorem 6: some unspecified `c > c*` via Example 4). No later arXiv paper moves the frequency constant. Wikipedia (fetched tonight) still quotes 0.38271. Tian arXiv:2608.25147 proves the empty-set-free form at poset height ≤ 4; that is a finite classification of a different parameter, not a frequency dent, and it is not claimed here.

The 2026-08-17 `first_crossing.json` already had Example-4 best at `β = 0.3825` with mesh crossing 0.382988, and said `c(β)` was still increasing at 0.40. The claimed number used `β = 1/5`. The leftover handle was the rest of the β interval.

### 1-D formula

On `{b,1}` the worse Example-4 C3 endpoint is always the independent one, so

    ratio = (1−a) Hmix(b,β) / h(b),

and the first mean with ratio < 1 is

    c(β) = min_b  1 − (1−b) h(b) / Hmix(b,β).

`compute/q1/scan_beta.py` evaluates this on `β ∈ [0,1]`. The curve is strictly increasing. At `β = 1`, Hmix = 1 on the whole interval `(1−1/√2, 1/2]`, and `c(1) = 0.3830513565868…`. Adding Sawin's max-entropy term does not beat pure Example 4 on this ray.

### Analytic crossing

For `b ∈ (1−1/√2, 1/2]`, Example 4 saturates `Π_{b,b}(0,0) = 1/2`. The first-crossing is therefore the unique critical point of `f(b) = 1 − (1−b)h(b)`:

    h(b) = (1−b) log₂((1−b)/b).

mpmath dps=80: `b* = 0.296493923569337…`, `c = 0.38305135658682558…`, residual `10^{-81}`, `g''(b*) < 0`. The 2026-08-17 closed form `1 − h(2^{-1/2})/√2 ≈ 0.383099` is `f` at the left endpoint `b = 1−1/√2`, not the minimum. The nearby Sawin-type point they treated as a failure is this critical point, and it is still above 0.38285.

### Claimed number

**0.38304**, strictly below the analytic crossing. On the 4500×3500 mesh, every cell with mean `≤ 0.38304` has ratio `≥ 1.000021687`. Independent C nested-loop mesh: same min ratio, 0 bad cells, same arg. Replay `compute/q1/run_all.sh`.

This is a dent of the repo ray-record 0.38285 and of Liu's published 0.382709, in the same `{b,1}` hypothesis class. It is not 1/2 and not every measure.

### Mixture residue

`hunt_two_atomic.py` at `(β,c) = (1, 0.38304)`: 13556 uniform 2-atomic samples, worst ratio 1.00195; 10077 near-ray perturbations, worst 1.00142; **0 hits** below 1. Incomplete search, not a Krein–Milman certificate.

### What we claim / do not claim

Claim: on `{b,1}`, pure Example 4 has Gilmer ratio ≥ 1 whenever the mean is at most 0.38304. The exact first-crossing of the ray is the analytic number 0.3830513565868….

Do not claim: the 1/2 conjecture; every measure on [0,1]; a new `n` or `|F|` classification; Tian's height-4 theorem (already published); Liu's PSD hypothesis.

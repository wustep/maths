# P_max error replacements (q4 work)

Context: compact certificate at `R=12`, `n=22` gives
`φ_target=0.9055`, `P=(q−1)/(q+1)≈0.0564`, `err=P(1−fmin)≈0.00597`,
`γ=0.899526`, `1/γ≈1.1118`.  Reweighting step:
`I/D = Σ_i s_i w_i λ_i / Σ_i s_i w_i` with `w_i=c_i μ_i`,
`s_i∈[1/q,q]`, `λ_i=Σ_j F_{ij}μ_j∈[fmin,1]`, `φ(μ)` the `s≡1` value.

Not a dent. No `h(D_L,D_R)` tail.

---

## 1. Replace `(1−fmin)` by `λ_max` or a pair-aware amplitude?

### 1a. Uniform `P·(λ_max − fmin)` with `λ_max<1`

**No** as a global replacement for `P(1−fmin)`.

- For any bin `i`, `F_{ii}=1` (same-bin pair hits `t=1`), so a vertex
  `μ=e_i` has `λ_i=1`.  Hence `max_i λ_i(μ)=1` on a set of measures that
  still matters for the certified `φ` inf.
- At those vertices the reweighting drop is **zero** (only one active
  `w_i`), so the error term is slack, but a **uniform** certificate must
  use amplitude `1−fmin`, not `λ_max−fmin<1−fmin`, if it is to hold for
  every `μ` without a state-dependent bookkeeping.

### 1b. Per-`μ` spread `P·(max_i λ_i − min_i λ_i)`

**Yes (conditional)** — plausible valid tightening; no counterexample found.

**Lemma (target).** Fix `μ`.  With `λ_i=(Fμ)_i`, `w_i=c_iμ_i`,
`s_i∈[1/q,q]`:
\[
  \phi(\mu)-\min_s \frac{\sum_i s_i w_i \lambda_i}{\sum_i s_i w_i}
  \;\le\; P\,\Big(\max_i\lambda_i-\min_i\lambda_i\Big).
\]
*Proof idea.*  `Q(s)` is a weighted mean of the numbers `λ_i` with
weights `t_i=s_i w_i`; varying `s` only scales each weight by a factor
in `[1/q,q]`.  For **equal** `w_i`, the sharp two-level adversary gives
drop `=P·(\max λ−\min λ)` (the classical `(κ−1)/(κ+1)` bound with
`κ=q`).  Unequal `w_i` can **decrease** the drop (e.g. two-bin equal
`w`: drop `=0` while spread `>0`), never increase it above `P·`spread in
exhaustive `n≤8` vertex searches (`max` ratio `≈0.9996` at `n=3`, still
`≤1`).

**Numerics at `R=12,n=22` (`pmax_try.py`, `reweight_gap.py`):**

| error term | value | `γ` if `φ=0.9055` |
|------------|-------|-------------------|
| `P(1−fmin)` | `0.00597` | `0.89953` |
| `P·spread(μ*)` at SLSQP `μ*` | `0.00262` | `0.90288` |
| `P·(λ_max(μ*)−fmin)` | `0.00319` | `0.90231` |

`μ*` is the SLSQP minimizer of `φ`; spread bound beats `λ_max−fmin`
because `min_i λ_i > fmin` there.

**Pair-aware without adversarial independence of `s` and `λ`:** **Yes,
this is exactly the spread bound.**  Correlation helps: large
`w_i/w_j` kills reweighting freedom (drop `→0`), while large spread
requires spread `μ` where the effective weights on competing bins are
moderate.  The adversarial **two-valued `s`** construction is sharp for
the amplitude but **pessimistic** for the compact grid (positive slack in
`reweight_gap.json`: `≈0.0067` at `R=12`).

**Counterexample to spread bound:** **not found.**  Saturating configs
exist (`n=3`, ratio `drop/(P·spread)≈1`), so spread is nearly sharp, not
loose.

**Caveat for certification:** faces certify `φ(μ)≥φ_target` uniformly;
replacing the error requires a **uniform** proof of the spread lemma
with varying `w_i=c_iμ_i`, not only grid search.  Until that is written,
treat `P·spread(μ*)` as **numerical residue**, not a new certificate.

---

## 2. `F_hi` on diagonal / nearby, `F_lo` on far bins?

**No** — cannot lower-bound `I` with `F_hi` on any pair.

- Valid kernel entries must satisfy `K_{ij} ≤ min_{(r,u)\in bin_i×bin_j} f(r/u)`.
  `F_hi[i,j]` is an **upper** endpoint of the interval enclosure; using it
  when `F_hi>F_lo` would **inflate** the quadratic lower bound and is
  unsound.
- On the certified mesh `R=12,n=22` (and `R=4,n=18`): **`F_hi=F_lo`
  pointwise** on every pair (`max(F_hi−F_lo)=0`).  A near/far split
  collapses to the same matrix already used in `A_lo`.
- Conceptually, near pairs already carry the tight per-pair minima in
  `F_lo`; the loss in `P(1−fmin)` is from **reweighting** `s`, not from
  slack in diagonal `F_{ii}` (already `1`).

---

## Scripts

- `pmax_try.py` — spread / `λ_max` savings at `μ*`, mixed-`F` sanity,
  random counterexample scan (no violation with ratio `>1` in tested
  regimes).

---

## Bottom line

| idea | verdict |
|------|---------|
| `P(λ_max−fmin)` uniform | **No** (`λ_max=1` on vertices) |
| `P·spread(μ)` per `μ` | **Yes (conditional)** — best candidate; ~`+0.0034` on `γ` at `R=12` if proved |
| pair-aware / no independence | **Yes** — use spread, not `(1−fmin)` |
| `F_hi` near / `F_lo` far | **No** — unsound; zero slack on current mesh |

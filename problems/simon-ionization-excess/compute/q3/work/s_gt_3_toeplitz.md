# s>3 and the Newton–Toeplitz average — residue

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1. Opened this
session: the [abs](https://arxiv.org/abs/2504.18487) and the
[HTML](https://arxiv.org/html/2504.18487v1), Theorem 2.2, Remark 2.3,
Lemma 4.3, Proposition 4.5, Lemma 5.9, and the proof of Theorem 2.2
in §7. Replay: `python3 toeplitz_probe.py` (writes
`toeplitz_probe.json`). No face enumeration, no `verify_beta3.c`.

Status: residue. No path to `b(4)` in Theorem 2.2. No global
`γ > fmin` on every radial probability. The compact-aspect number
`0.901924` (leading `1.1087` on aspect `≤ 4`) is not used and is
not unrestricted.

## A. `s>3`: the two-shell sign, and nothing else feeds `b(4)`

q2 already had the closed quadratic. Independently:

```
Q_s(α, β; t, ℓ) = α² t^{s−1} + β² + αβ (t^{s+ℓ} + t^ℓ).
```

At `s=4`, `ℓ=1`, `t=1/8`, `α=16`, `β=−1` this is the dyadic
rational

```
16² · (1/8)³ + 1 − 16 · ((1/8)⁵ + 1/8)
  = 256/512 + 1 − 16/32768 − 2
  = −1/2 − 1/2048
  = −1025/2048 < 0.
```

The same opposite, inner-heavy dipole is negative at `s=7/2`
(`1/√2 − 1 − 1/(65536√2) < 0`) and at `s=3.1`. At `s=3` the
discriminant is the identity

```
(t⁴ + t)² − 4 t² = t² (t³ − 1)(t³ + 3) ≤ 0    on (0, 1],
```

so the dipole form stays nonnegative. One-shell, same-sign, and
quadrupole (`ℓ=2`, Hardy threshold `5`) stay positive on `(3, 4]`.
Interval enclosures sit in `compute/q2/certs/s_gt_3.json`; this
folder only replays the algebra.

That kills Lemma 4.3 for every `s>3`: there exist measures
orthogonal to radial functions with `I_s(ν) < 0`, so
`I_s(ρ)` need not dominate `I_s(ρ̄)`.

### Does any other HPS path justify `b(4) ≈ 1.083` in Theorem 2.2?

No. The printed chain is short, and the missing piece is only
`β_4 ≥ b(4)^{-1}`.

Theorem 2.2 is `N_c < b(s) Z + c(s) Z^{1/3}` for `s ∈ (1, 3]`.
The §7 proof solves the Lemma 5.9 comparison (5.50) for `N` and
substitutes the Proposition 4.5 floor `β_s ≥ b(s)^{-1}`. Lemma 5.9
already runs for `2 ≤ s ≤ 4`. It compares `α_{N,s}` to `β_s`. It
does not produce a lower bound on `β_s`. On `(3, 4]` it has
nothing to feed into unless someone else supplies
`β_s ≥ b(s)^{-1}`.

Proposition 4.5 without Lemma 4.3 still gives
`β_s^{rad} ≥ b(s)^{-1}` for every `s>1`, by Newton and the
elementary minimum of `(1+t^s)/(1+t^{s−1})`. Theorem 2.2 consumes
the full `β_s` (infimum over all probabilities in `D_s`), not the
radial infimum. Lemma 5.9 is written with that full `β_s`.
Substituting `β_4^{rad}` would be a different lemma.

The other candidates in the paper, or next to it, do not close
the gap:

- Remark 2.3 conjectures that Theorem 2.2 holds for all `s ≥ 1`
  with the same `b(s)`. It is a conjecture. Remark 4.6 says
  explicitly that they do not know whether the Proposition 4.5
  floor extends past `s=3`.
- Remark 4.4: there is no positive-definiteness argument for
  `I_s` when `s>0`. The two-shell examples show more: on
  `{ν ⊥ radial}` the form `I_s` is not positive, and not
  conditionally positive, for any tested `s>3`. The Coulomb
  argument of Remark 4.4 (`I_0(ρ) = I_0(ρ̄) + I_0(ν) ≥ I_0(ρ̄)`)
  has no analogue at `s=4`.
- IMS plus Hardy is the only proof of Lemma 4.3 in the paper.
  The improved constant is `c_H = 9/4`, so `c_H − s²/4 ≥ 0`
  only for `s ≤ 3`. Hardy on `V` itself (quotient near `9/2`)
  is the wrong object; q2 already recorded that. A quadrupole
  restriction would allow `s ≤ 5`, but a general `ν ⊥ radial`
  has an `ℓ=1` piece, and the many-body density is not so
  restricted.
- The pointwise minorant `|x−y| ≤ 2 max(|x|,|y|)` gives
  `β_4 ≥ (1/2) b(4)^{-1} ≈ 0.4617`, hence a leading coefficient
  at most `2.17`, worse than Lieb.
- A small dipole modulation of a radial probability has
  `I_4(ρ) = I_4(ρ̄) + ε² I_4(ν) < I_4(ρ̄)` whenever `I_4(ν)<0`.
  That shows the radial infimum is not the full infimum. It does
  not prove `β_4 < b(4)^{-1}`, and it does not prove
  `β_4 ≥ b(4)^{-1}` either.

No other comparison in HPS (Newton for non-radial measures,
multipole remainder, Lemma 5.5, the kinetic remainder in §6)
replaces `β_4 ≥ b(4)^{-1}`. A new pair estimate that never
passes through `β_4` would be a different paper. None is
certified here. `b(4) ≈ 1.0830249` is smaller than `1.1185`
and cannot be used in Theorem 2.2.

## B. After Newton, `Q` is an average of `f` — no cheaper floor

For a radial probability, Newton gives

```
g(r,u) = (r³ + u³) / (2 max(r,u)) = f(t) (r² + u²) / 2,
t = min(r,u) / max(r,u),    f(t) = (1 + t³) / (1 + t²).
```

So `Q = I/D` is a weighted average of `f`. In particular
`Q ≥ fmin = 1/b(3) ≈ 0.89410745697`, which is Proposition 4.5
at `s=3`. Figure 2 already says this is not sharp: the HPS
power-law trial sits near `0.9207`. A global `γ > fmin` would
move the leading coefficient below `b(3)`. Three cheap attempts
do not produce one.

### Two-atom exact minimum

Two radii, ratio `t ∈ (0,1]`, D-mass `w` on the inner atom.
The quotient is

```
Q(w,t) = [w² + (1−w)² t² + w(1−w)(1+t³)] / [w + (1−w)t²].
```

For fixed `t` the unique interior critical point is `w = t/(1+t)`,
and

```
Q2(t) = (1 + 2t + t³) / (1 + 2t + t²).
```

`Q2'(t) = 0` on `(0,1)` at the positive root of `t² + 3t − 2 = 0`,

```
t* = (−3 + √17) / 2 ≈ 0.5615528128,
Q2* = (17√17 − 55) / 16 ≈ 0.9432997272,
1/Q2* = (55 + 17√17) / 118 ≈ 1.0601084376.
```

That coefficient is below `1.1185`. It is a lower bound only for
2-atomic measures. q2's 3-atomic search already has
`I/D ≈ 0.931 < Q2*`. The two-atom floor is not global.

At the HPS ratio `t0` one has the identity `t0³ = 2 − 3 t0`, so

```
Q2(t0) = (3 − t0) / (1 + t0)² ≈ 0.94366,
```

slightly above `Q2*`. The pairs that saturate `f = fmin` are not
the two-atom minimizer.

### Infinite `t0`-chain

Equal `m`-mass on `r_k = t0^{-k}`, `k = 0, …, n−1`. With
`u = t0^{-2}` the energy is a finite geometric sum,

```
D = (1/n) (u^n − 1)/(u − 1),
I = (1/n²) Σ_d f(t0^{|d|}) · ((1 + u^d)/2) · (u^{n−|d|} − 1)/(u − 1).
```

The `n=3` line collapses to

```
Q3 = (1/3) [ 1 + fmin (1+u)²/(1+u+u²) + f(t0²) (1+u²)/(1+u+u²) ]
   ≈ 0.9379263180.
```

That is the minimum of the family: `Q1 = 1`, `Q2 ≈ 0.94705`,
`Q3 ≈ 0.93793`, then `Q_n` increases (`Q24 ≈ 0.98823`). Equal
D-mass is the inversion of equal `m`-mass on a geometric set and
gives the same `Q_n`.

The `n → ∞` limit is `1`, not `fmin`. Write `Q = 1 − (1/n) Δ / Σ u^k`
with `Δ = Σ_{i,j} (1 − f_{|i−j|}) (u^i + u^j)/2`. Both `Δ` and
`Σ u^k` are `O(u^n)`, so the deficit is `O(1/n)`. A long
`t0`-chain does not put almost all pair-weight at `t0`: either
`n` is small and the `t=1` self-pairs stay large, or `n` is large
and the `1/n` masses kill the deficit.

`Q3 ≈ 0.9379` is a trial, hence an upper bound on `β_3^{rad}`.
It sits above the HPS power-law `0.9207`. It is not a lower
bound, and it does not beat `1.1185` as a global coefficient.

### 1D convolution on log-radius

Put `x = log r`. Then

```
I = ∬ f(e^{−|x−y|}) (e^{2x} + e^{2y})/2 ρ(dx) ρ(dy),
D = ∫ e^{2x} ρ(dx),
```

for a probability `ρ` on the line. The translation-invariant
kernel `K(h) = f(e^{−|h|})` satisfies `K ≥ fmin`, with equality
only at `|h| = −log t0`. Any average of `K` is therefore
`≥ fmin`. That is again Proposition 4.5. There is no Bochner
gap: `K(h) − γ` is not a positive-definite bump for any
`γ > fmin`, because `K(∞) = 1` and `K` attains `fmin` at two
finite points.

Dropping positivity makes it worse. The truncated Toeplitz
symbol of `K` on a 16-point `t0`-step grid, evaluated at
`θ = π`, is `≈ 0.11187 < fmin`. Signed log-densities are not a
path to a higher floor.

Positive trials on at most 16 log-nodes (the cap here):

- two bumps at distance `−log t0`: unweighted energy
  `(1 + fmin)/2 ≈ 0.94705`;
- three equal bumps at `0, h0, 2h0`: `≈ 0.93688`;
- log-Gaussians, `n = 16`: best `Q ≈ 0.92360` at `σ = 0.4`,
  still above the power-law `0.9207`;
- log-uniform `m` (i.e. `m(dr) ∝ dr/r`) on aspect `2` through
  `12`: best in the scan `≈ 0.92267` at aspect `3.5`.

None of these is a lower bound. None of them raises the global
floor above `fmin`. A number that does not beat `1.1185`
globally is not a dent of the printed leading coefficient.

The leftover handle is unchanged: a proof that a minimizer has
bounded aspect, or any other argument that gives `Q ≥ γ > fmin`
for every radial probability. The compact-class certificate
`Q ≥ 0.901924` on aspect `≤ 4` is not that argument.

## What is proved vs still open

Proved here: the q2 two-shell sign at `s=4` is the exact
rational `−1025/2048`; Lemma 4.3 does not extend; Lemma 5.9,
Newton-on-radial, pointwise `|x−y| ≤ 2 max`, and signed
convolution do not justify feeding `b(4)` into Theorem 2.2;
the two-atom min is `(17√17 − 55)/16` and is not global; a
`t0`-chain has closed form `Q_n → 1` with minimum `Q3 ≈ 0.9379`
and is a trial; the log-radius kernel recovers `fmin` as a
global floor and nothing strictly above it.

Not proved: `β_s ≥ b(s)^{-1}` for any `s>3`; `β_s < b(s)^{-1}`;
a global `γ > fmin` for `β_3^{rad}`. Not a dent of `1.1185`.
Remark 2.3 remains a conjecture. The compact-class `1.1087` is
not unrestricted.

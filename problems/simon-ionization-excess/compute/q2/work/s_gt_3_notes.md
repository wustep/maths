# s > 3: radialization fails

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, Lemma 4.3 and
Proposition 4.5. Opened this session: the [abs](https://arxiv.org/abs/2504.18487)
and the [HTML](https://arxiv.org/html/2504.18487v1), §4 and Lemma 5.9.
Replay: `python3 s_gt_3.py` or `./run_s_gt_3.sh` (writes `certs/s_gt_3.json`).

## Result

`I_s(ν)` goes negative for every tested `s > 3` on an explicit family
of measures orthogonal to radial functions. There is no certified
path to `s > 3` along the HPS argument. The function `b(4)` from
(2.7) is

```
b(4) = 1.08302491750762443520… ∈ (1.08302, 1.08303).
```

That number is smaller than the printed leading coefficient `1.1185`,
but it cannot be used in Theorem 2.2: Lemma 4.3 does not extend, so
Proposition 4.5 does not give `β_4 ≥ b(4)^{-1}`.

Status: residue. Not a dent of `1.1185`.

## What HPS need

Lemma 4.3: `I_s(ρ) ≥ I_s(ρ̄)` for `s ∈ (1, 3]`, where

```
I_s(μ) = ∬ (|x|^s + |y|^s) / (2 |x−y|) dμ(x) dμ(y).
```

The cross term against the radial part vanishes by Newton. The claim
reduces to `I_s(ν) ≥ 0` for `ν = ρ − ρ̄`, which is orthogonal to
every radial function. IMS plus the improved Hardy constant
`c_H = d²/4 = 9/4` (Ekholm–Frank 2006, Lemma 2.4; HPS (4.15)) gives

```
I_s(ν) ≥ (9/4 − s²/4) × (a nonnegative remainder).
```

The prefactor is nonnegative only for `s ≤ 3`. Remark 2.3 conjectures
that Theorem 2.2 still holds for all `s ≥ 1` with the same `b(s)`.
Lemma 5.9 already compares `α_{N,s}` to `β_s` for `2 ≤ s ≤ 4`. The
missing piece on `(3, 4]` is radialization.

Proposition 4.5 itself, *if* one already has `I_s(ρ) ≥ I_s(ρ̄)`, is
not restricted to `s ≤ 3`: Newton and the elementary minimum of
`(1 + t^s)/(1 + t^{s−1})` work for every `s > 1`. The obstruction is
only Lemma 4.3.

## Two-shell spherical harmonics

Put surface densities `α Y_{ℓm}` and `β Y_{ℓm}` on spheres of radii
`t ∈ (0, 1]` and `1`. This is orthogonal to every radial test function
for `ℓ ≥ 1`, and it lies in `H^{-1}`. The Coulomb potential is
elementary. With `Y_{ℓm}` L²-normalised on `S²`,

```
I_s(ν) = [4π / (2ℓ+1)] Q_s(α, β; t, ℓ),
Q_s    = α² t^{s−1} + β² + αβ (t^{s+ℓ} + t^ℓ).
```

`Q` has a negative eigenvalue if and only if
`(t^{s+ℓ} + t^ℓ)/2 > t^{(s−1)/2}`. For small `t` this is the comparison
of `t^ℓ` with `t^{(s−1)/2}`, i.e. `s ≷ 2ℓ+1`. That is exactly the
Hardy threshold for angular momentum `ℓ`:
`∫ |∇u|² ≥ (ℓ(ℓ+1) + 1/4) ∫ u²/|x|²`, so
`s ≤ 2√(ℓ(ℓ+1)+1/4) = 2ℓ+1`.

Dipole `ℓ = 1`: threshold `s = 3`. Quadrupole `ℓ = 2`: threshold
`s = 5`, so two-shell quadrupoles stay nonnegative on `(3, 4]`.

At `s = 3`, `ℓ = 1` the discriminant is an identity,

```
(t⁴ + t)² − 4 t² = t² (t³ − 1)(t³ + 3) ≤ 0    for t ∈ (0, 1],
```

so `Q ≥ 0` for every real `(α, β)`. Interval arithmetic on the
examples in the certificate agrees.

## Certified negatives

Opposite-sign, inner-heavy dipoles:

| s | t | α | β | Q | sign |
| --- | --- | --- | --- | --- | --- |
| 3 | 1/2 | 1 | −1 | 11/16 | + |
| 3 | 1/10 | 20 | −1 | 2.998 | + |
| 3.1 | 10^{-7} | 3·10^7 | −1 | −0.20426… | − |
| 7/2 | 1/32 | 64 | −1 | `1/√2 − 1 − 1/(65536√2)` | − |
| 4 | 1/8 | 16 | −1 | **−1025/2048** | − |

The `s = 4` line is a dyadic rational:

```
16² · (1/8)³ + 1 − 16 · ((1/8)⁵ + 1/8)
  = 1/2 + 1 − 2 − 1/2048
  = −1025/2048 < 0.
```

The `s = 7/2` line is negative because `1/√2 − 1 < 0`. Both sit in
`certs/s_gt_3.json` as interval enclosures and as these closed forms.
A Fibonacci-sphere pairwise sum at `s = 4`, omitting the same-shell
diagonal (a positive self-energy), is already negative, so the sign
does not come from a multipole-algebra slip.

Thin radial Gaussians around the same two radii, same weights, give
the same signs as volume densities: `I_4 < 0`, `I_{3.5} < 0`,
`I_3 > 0`. So the surface-measure idealisation is not the source of
the negativity.

## The listed one-scale examples stay positive

These are the measures named in the brief. All are orthogonal to
radial functions. None of them makes `I_s` negative for `s ∈ {3, 3.1, 3.5, 4}`.

- Pure dipole, `R(r) = r e^{-r}` times `Y_{10}` (one-sign radial
  profile). `I_s > 0`.
- Pure quadrupole, `R(r) = r² e^{-r}` times `Y_{20}`. `I_s > 0`.
- One-shell `Y_{ℓm}`, any `s`. Here `|x|^s` is constant, so
  `I_s = R^s I_0` and Coulomb is positive definite.
- Two opposite Gaussians at `±μ e_z` (regularised opposite Diracs,
  same radius). `I_s > 0` on the three widths that were integrated.
- Same-sign two-shell dipole. The quadratic form has positive
  coefficients on the diagonal and the cross term; `Q > 0`.
- Two-shell quadrupole, opposite weights, `s ≤ 4 < 5`. `Q > 0`.

A generic sign-changing radial profile is not enough. The negative
mode wants a large inner dipole and a small opposite outer dipole,
with radius ratio past `t_* ∼ (1/4)^{1/(s−3)}`. For `s = 3.1` that
is `t ≲ 10^{-6}`. For `s = 4` it is `t < 1/4`. The two-exponential
`e^{-r} − e^{-r/8}` does not put enough weight on the inner scale
and stays positive.

## Hardy for Coulomb potentials

The informal hope is that `V = (−Δ)^{-1} ν` is not the Hardy
optimiser, so the constant in front of `∫ V²/|x|²` might exceed
`9/4` and buy an `s = 3+ε`.

Hardy on `V` itself is the wrong object. IMS applies Hardy to
`u = |x|^{s/2} V`. For every two-shell dipole in the table,
`Q_H(V) = ∫|∇V|² / ∫ V²/|x|²` sits at `4.5` or a few parts in
`10^2` above it (exactly `9/2` for a single shell). If one
mistakenly used `c_H = 9/2` on `V`, the threshold would look like
`s ≤ √18 ≈ 4.24`. That is not a proof: the identity is not Hardy
on `V`, and the closed form already gives `I_{3.1} < 0`.

The unregularized remainder `∫ |x|^{s−2} V²` diverges at infinity
for a dipole tail `V ∼ 1/r²` as soon as `s ≥ 3`. HPS know this —
they replace `|x|^s` by `|x|^s/(1+ε|x|^s)` before IMS. After that
cutoff the only uniform constant they have is `9/4`, and the
examples show it is sharp in the dipole sector: for every `s > 3`
there is a `ν` with `I_s(ν) < 0`. There is no uniform `s = 3+ε`.

A quadrupole-only restriction would allow `s ≤ 5`, but a general
`ν ⊥` radial has an `ℓ = 1` piece.

## `β_s` without radialization

A lower bound on `β_s` is what Theorem 2.2 consumes. A search is
an upper bound.

The pointwise minorant
`(|x|^s+|y|^s)/(2|x−y|(|x|^{s−1}+|y|^{s−1}))`
equals `(1+t^s)/(1+t^{s−1}) · max(|x|,|y|) / (2|x−y|)`. The geometry
factor is at least `1/2`, so

```
β_s ≥ (1/2) b(s)^{-1}.
```

For `s = 4` that is `β_4 ≥ 0.46166…`, hence a leading coefficient
at most `2.17`, worse than Lieb. The `|x−y|` in the denominator is
why a pointwise bound does not beat `1.1185`.

Trials (upper bounds only, `certs/s_gt_3.json`):

- Two shells with angular modulation `1 ± ε cos θ`, `|ε| ≤ 1` so
  the measure stays a probability: `β_{3.5} ≤ 0.969`,
  `β_4 ≤ 0.972`. Both sit above `b(s)^{-1}`.
- Nam-like radial `r^{-p}` on `[1, n]`, Newton: `β_{3.5}^{rad} ≤ 0.937`,
  `β_4^{rad} ≤ 0.950`. Still above `b(s)^{-1}`, as they must
  (`β_s^{rad} ≥ b(s)^{-1}` for every `s`, no radialization required).

None of these is a lower bound. None of them shows
`β_s < b(s)^{-1}`. The negative `I_s(ν)` does show that a
probability `ρ = ρ̄ + εν` with a small opposite-dipole modulation
has `I_s(ρ) < I_s(ρ̄)`, so the radial infimum is not the full
infimum. Whether the drop crosses `b(s)^{-1}` is open. Crossing it
would make the Remark 2.3 coefficient strictly too small for this
proof; it would not, by itself, produce a new ionization upper bound.

## `b(s)`

```
b(s) = max_{t∈[0,1]} (1 + t^{s−1}) / (1 + t^s) = (s−1) / (s t_0),
t_0^s + s t_0 + 1 − s = 0.
```

| s | t_0 | b(s) | b(s)^{-1} |
| --- | --- | --- | --- |
| 3 | 0.59607163798… | 1.11843379920… | 0.89410745697… |
| 3.1 | 0.60832308192… | 1.11358482849… | 0.89800073997… |
| 3.5 | 0.65076486502… | 1.09760952485… | 0.91107081103… |
| 4 | 0.69250484257… | 1.08302491751… | 0.92333979010… |

`b(3)` matches the q1 replay of (2.9). `b(4)` matches a 20 000-point
grid maximum of `(1+t³)/(1+t⁴)` to `10^{-8}`, and the root of
`t⁴ + 4t − 3 = 0` is isolated in a tiny interval before the
quotient is evaluated.

## What is proved vs still open

Proved here: Lemma 4.3 does not extend past `s = 3`. Explicit
`ν ⊥` radial have `I_s(ν) < 0` for every `s ∈ {3.1, 3.5, 4}`,
with a rational certificate at `s = 4`. The improved-Hardy gap
cannot be opened uniformly for Coulomb potentials of such `ν`.

Not proved: a lower bound on `β_s` for `s > 3` other than the
useless `(1/2) b(s)^{-1}`. Not proved: `β_s < b(s)^{-1}`. Not a
dent of the printed `1.1185`. Remark 2.3 remains a conjecture.
Lemma 5.9 on `(3, 4]` has nothing to feed into if `β_s` is not
bounded from below by `b(s)^{-1}`.

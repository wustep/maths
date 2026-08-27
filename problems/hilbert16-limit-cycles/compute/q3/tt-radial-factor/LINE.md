# Line TT — radial factor (x²+y²)X

Status: two-cycle dent dropped. Fork kept. Not a dent of
H(5) ≥ 37.

Imagined: apply the Gasull–Santana §4 remark to the radial
cubic and write an explicit degree-5 field with two hyperbolic
cycles, hence H(5) ≥ 2.

Dropped: the unperturbed field Y = (x²+y²)X still has one
positive periodic orbit, the same circle r = ρ. A perturbation
that births a second cycle is not written. One cycle in degree
5 is H(5) ≥ 1, not a +1, and 2 would not beat the published
H(5) ≥ 37 anyway.

Replay:

```
problems/hilbert16-limit-cycles/compute/q3/tt-radial-factor/run.sh
```

Python expands the identities sparsely; Rust expands them
again and evaluates the polar residuals on the integer box
from −3 to 3. The two dumps are `diff`ed. Exit 0. Certs:
`certs/identities.json`, `certs/core.json`.

Opened this session:
[arXiv:2407.13465v2](https://arxiv.org/abs/2407.13465) and its
[HTML](https://arxiv.org/html/2407.13465v2) (§4 remark after
Theorem 1; the line-multiplication proof of H(n+1) ≥ H(n)+1
is Theorem 1 in §3).

## Dropped — two hyperbolic cycles, hence H(5) at least 2

Section 4 of Gasull–Santana, arXiv:2407.13465v2, remarks that
if X has degree n then Y = (x²+y²)X has degree n+2 and is
equivalent to X except at the origin, where it has an extra
degenerate singularity. They say a small perturbation of Y
creates an extra cycle, hence

$$H(n+2)\ge H(n)+1,$$

which they call much easier than the line-multiplication
theorem H(n+1) ≥ H(n)+1.

The imagined certificate was that remark applied to the
radial cubic of q1 line D, producing an explicit degree-5
field with two hyperbolic isolated periodic orbits.

That field is not written. The unperturbed Y is written, and
it has one cycle, not two. A numeric or existential
perturbation is not a lower bound. Two cycles would still
lose to Prohens–Torregrosa H(5) ≥ 37
(Nonlinearity 32, 2019). The dent is dropped.

## Kept — polar identities, unique cycle r = ρ, degree 5

The radial cubic X, with ρ² = 1/4 in the specialized field,
is

$$\dot x = y-x(x^2+y^2-\rho^2),\qquad
\dot y = -x-y(x^2+y^2-\rho^2).$$

Its polar form is ṙ = r(ρ² − r²), θ̇ = −1. Unique cycle
r = ρ (q1 line D). Set Y = (x²+y²)X. In Z[x, y, ρ] the
identities (certificate block `polar`) are

$$xP_Y+yQ_Y=(x^2+y^2)^2(\rho^2-x^2-y^2),\qquad
xQ_Y-yP_Y=-(x^2+y^2)^2.$$

These are r ṙ = r⁴(ρ² − r²) and r² θ̇ = −r⁴, i.e.

$$\dot r = r^3(\rho^2-r^2),\qquad \dot\theta = -r^2.$$

The radial speed factors as
r³(ρ² − r²) = r³(ρ − r)(ρ + r) (block `radial_speed`).
Consequences, none of which needs a computer:

- Off the origin, θ̇ = −r² ≠ 0, so Y cannot vanish.
  The only equilibrium is the origin. The 2-jet of Y at
  the origin is zero; the 3-jet is not (jet order 3).
  For X the jet order is 1. The origin of Y is more
  degenerate, as the remark says.
- The only positive root of ṙ = 0 is r = ρ. The origin
  r = 0 is an equilibrium, not a periodic orbit.
- On the circle r = ρ one has ṙ = 0 and θ̇ = −ρ² ≠ 0,
  so the orbit is periodic.
- On (0, ρ) one has ṙ > 0; on (ρ, ∞) one has ṙ < 0.
  The circle is invariant. A periodic orbit cannot live
  in either open annulus, because r is strictly monotone
  there. Hence the circle is the only positive periodic
  orbit of the unperturbed Y.

The derivative of g(r) = r³(ρ² − r²) at r = ρ is
−2ρ⁴ ≠ 0, so the cycle is hyperbolic. Degree of Y is
exact 5: the degree-5 part is −(x²+y²)²(x, y) (block
`leading`), which does not vanish.

At ρ² = 1/4 the same statements hold in Z[x, y] after
clearing the denominator 4 (block `specialized`). The
cleared radial speed is r³(1 − 4r²) = r³(1 − 2r)(1 + 2r),
unique positive root r = 1/2. Degree still 5.

This is one hyperbolic cycle of an explicit degree-5
field: H(5) ≥ 1. It is not a +1 until a second cycle is
certified. It does not touch the published record
H(5) ≥ 37.

## Kept — line-multiplication is degree n+1; this is n+2

Theorem 1 of the same paper multiplies X by a line
ax + by through a regular point translated to the origin,
then perturbs the line of singularities. That construction
has degree n+1. Line KK is that map. This line is the
§4 factor, degree n+2.

On the radial cubic, the sample line L = x + y gives a
degree-4 field (block `line_multiplication`):

$$xP_L+yQ_L=(x+y)(x^2+y^2)(\rho^2-x^2-y^2),\qquad
xQ_L-yP_L=-(x+y)(x^2+y^2).$$

Degree 4 = n+1. The radial factor has degree 5 = n+2.
The sample line is only a degree comparison. It is not
the Theorem 1 field (the origin of the radial cubic is
already an equilibrium, so it is not the regular point
of that construction).

The §4 remark is easier than Theorem 1 as an existence
argument for H(n+2) ≥ H(n)+1. Applied here, the
unperturbed Y still has one cycle. The extra cycle of
the remark is a perturbation that this folder does not
write.

## What this is not

Not a dent of H(5) ≥ 37. Not an explicit field with two
hyperbolic cycles. Not a certification of the +1 in
H(n+2) ≥ H(n)+1. Not Theorem 1 (that is degree n+1).
The reusable lemma is the pair of polar identities for
Y and the uniqueness of r = ρ. A stranger can run
`run.sh` and read degree 5 and H(5) ≥ 1 off the dump.

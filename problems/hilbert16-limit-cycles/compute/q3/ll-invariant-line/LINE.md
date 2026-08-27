# Line LL — cubic with an invariant line and three cycles

Status: imagined three isolated cycles dropped. Fork kept. Not a
dent of `H(3)`.

Imagined certificate. An explicit cubic with a straight-line
solution has three isolated periodic orbits.

Drop immediately. No three-cycle cubic is written. Ye / Cherkas
uniqueness (at most one cycle) is a theorem for quadratics with
an invariant line, not for cubics. Cubics with a line remain
open. A linear Dulac factor along the line, on the named family
below, does not produce three cycles: it produces zero.

Fork kept. One named cubic with a genuine invariant line (not a
line of equilibria) and a certified isolated-cycle count of 0
for that family, by Bendixson–Dulac. Symbolic only. Fractions as
strings. Not a bound on `H(n)`.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/ll-invariant-line/run.sh
```

Python expands the identities sparsely; Rust expands them again
and evaluates the residuals on the integer box from −3 to 3.
The two dumps are `diff`ed. Exit 0. Certs: `certs/core.json`,
`certs/identities.json`.

Opened this session:
[Scholarpedia, Han–Li–Li 2010](http://www.scholarpedia.org/article/Limit_cycles_of_planar_polynomial_vector_fields).
Lead, not a citation. The article records: Chen–Ye (class I)
and Cherkas–Zhilevich / Rychkov (class III with `a = 0`) give
that a quadratic with a straight-line solution has at most one
limit cycle. That is the quadratic context below. It is not
re-proved here, and it does not apply to degree 3.

## Dropped — three isolated periodic orbits

The fiction needs an explicit cubic field, a genuine invariant
line, and three isolated cycles. Ye / Cherkas do not forbid
that: their uniqueness theorem is for degree 2. Nothing in the
fetched record writes three cubic cycles on a line as a
replayable field, and this line does not invent one. A numeric
search, or a Poincaré–Bendixson picture without a certificate,
is not a lower bound.

The named field below is degree 3 and has an invariant line.
The count it certifies is 0, not 3.

## Context — quadratics, at most one (Ye / Cherkas)

A quadratic planar field with an invariant straight line has at
most one limit cycle. Scholarpedia records this as the union of
Ye class I (Chen–Ye) and the Cherkas–Zhilevich / Rychkov
treatment of class III with a vanishing `a`. Coppel’s survey
and later expositions quote the same uniqueness. This line does
not re-prove that theorem and does not replay Cherkas’s Abel
reduction. The object below is cubic.

## Kept — named cubic, invariant line y = 0

Named field, integer coefficients, degree 3:

$$\dot x=16y+16x+x^3,\qquad \dot y=16\,xy.$$

The same orbits as the μ-family member μ = 1/16,

$$\dot x=y+x+\tfrac{1}{16}x^3,\qquad \dot y=xy,$$

after a constant time rescaling (block `named`).

The polynomial y is a first integral of the line: the Lie
derivative is Q = 16xy = (16x) y, so the cofactor is 16x
(block `line`). Hence y = 0 is invariant. It is not a line of
equilibria. Restricting to y = 0 gives

$$\dot x=x(16+x^2),\qquad \dot y=0.$$

The factor 16 + x² is at least 16 (block `axis`; as a
polynomial, 16 + x² − 16 − x² ≡ 0 and the constant 16 is
nonzero). So P(x, 0) vanishes only at the origin. Sample:
P(1, 0) = 17.

Equilibria of the named field: Q = 0 forces x = 0 or y = 0.
On x = 0 one has P = 16y, so y = 0. On y = 0 one has
P = x(16 + x²), so x = 0. The only equilibrium is the origin
(block `equilibria`). The Jacobian there is

$$\begin{pmatrix}16&16\\0&0\end{pmatrix},$$

trace 16, determinant 0: one eigendirection along the invariant
line, as it must be. A focus cannot sit on an invariant line.

The one-parameter family, still degree 3 for μ ≠ 0,

$$\dot x=y+x+\mu x^3,\qquad \dot y=xy,$$

has the same invariant line y = 0 with cofactor x, and
P(x, 0) = x(1 + μ x²). For μ ≥ 0 the axis factor 1 + μ x² is
at least 1, so again the axis is not a line of equilibria
(block `family`).

A degeneration that was discarded: ẋ = y,
ẏ = −y(x + μ(x² − 1)y) has Q(x, 0) ≡ 0, but also P(x, 0) ≡ 0,
so the whole x-axis is equilibria (block `degeneration`). That
is not a genuine invariant line in the sense of this line.

## Kept — Dulac, certified count 0

Ordinary divergence of the named field is

$$\mathrm{div}\,X=16+16x+3x^2.$$

The discriminant of that quadratic is 16² − 4 · 3 · 16 = 64
(block `bendixson`). It changes sign: div(0, 0) = 16 and
div(−3, 0) = −5. Bendixson’s criterion on the plane is
inconclusive. The invariant line is used.

Take the Dulac function B = 1/y, which is C¹ and nonzero on
each open half-plane. The weighted divergence is

$$\mathrm{div}(BX)=\frac{1}{y}\,\mathrm{div}\,X-\frac{Q}{y^2}
=\frac{16+3x^2}{y}.$$

The polynomial identity behind the cancellation is

$$y\cdot\mathrm{div}\,X-Q=y(16+3x^2)$$

(block `dulac`; the xy terms cancel). The numerator
16 + 3x² is at least 16 and is not the zero polynomial. In
{y > 0} one has div(BX) > 0; in {y < 0} one has div(BX) < 0.
Each open half-plane is simply connected. Bendixson–Dulac:
neither half-plane contains a closed orbit.

A closed orbit of a C¹ field cannot cross an invariant line.
The restricted flow on y = 0 is one-dimensional and, as above,
has no periodic orbit. Therefore the named field has exactly
0 isolated periodic orbits.

The same Dulac works for the whole family μ ≥ 0. There

$$\mathrm{div}\,X=1+x+3\mu x^2,\qquad
y\cdot\mathrm{div}\,X-Q=y(1+3\mu x^2),$$

and 1 + 3μ x² ≥ 1 (block `family`). Certified isolated-cycle
count for the family: 0. When μ = 0 the field is quadratic
and Ye already gives at most one; the same Dulac gives zero
for this particular quadratic. That is not a proof of Ye.

When 0 < μ < 1/12 the unweighted discriminant 1 − 12μ is
positive, so ordinary Bendixson fails and the factor 1/y is
essential. The named cubic μ = 1/16 lies in that range.

The count 0 is an exact upper bound for this family, not for
every cubic with a line, and not for H(3). A different cubic
with a line might have cycles; this line does not produce one.

## What this is not

Not a bound on H(n). Not a dent. Not three cubic cycles. Not
a re-proof of Ye / Cherkas. Not a line of equilibria. The
reusable lemma is the named field and the Dulac identity: a
stranger can run `run.sh` and read the cycle count 0, the
line y = 0, and the cancelled numerator 16 + 3x² off the
JSON.

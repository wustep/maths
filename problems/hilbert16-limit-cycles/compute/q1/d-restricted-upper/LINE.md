# Line D — restricted exact upper bounds

Status: kept. `H(n)` did not move. This is not a dent of `H(3)`.

The primary lemma is an exact uniqueness statement for one cubic
family. Line C may use the same field as a seed and only needs
existence of a periodic orbit. This line owns uniqueness.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q1/d-restricted-upper/run.sh
```

Python expands the identities sparsely; Rust expands them again
and also evaluates the polar differences on the integer box
from -3 to 3 in each variable. A degree-at-most-4 polynomial in
three variables that vanishes on that box is zero. The two dumps
are `diff`ed. Exit 0.

## Kept — radial cubic, exactly one cycle

For every real rho with $0 < \rho < 1$, the cubic field

$$\dot x = y - x(x^2+y^2-\rho^2),\qquad
\dot y = -x - y(x^2+y^2-\rho^2)$$

has exactly one periodic orbit: the circle of radius $\rho$.

The same identities hold in the polynomial ring Z[x, y, rho]
with no restriction on rho. For every $\rho > 0$ the unique
periodic orbit is still that circle. The interval (0, 1) is the
sub-family named in the imagined end-state (a unit-disk seed).
If rho is zero the circle collapses to the origin and there is
no periodic orbit.

Polar form, as polynomial identities (certificate
`certs/identities.json`, block `polar`):

$$xP+yQ = (x^2+y^2)(\rho^2-x^2-y^2),\qquad
xQ-yP = -(x^2+y^2).$$

These are $r\,\dot r = r^2(\rho^2-r^2)$ and $r^2\dot\theta = -r^2$,
i.e.

$$\dot r = r(\rho^2-r^2),\qquad \dot\theta = -1.$$

Consequences, none of which needs a computer:

- The only equilibrium is the origin. Off the origin the angular
  identity gives $xQ-yP = -r^2 \ne 0$, so (P, Q) cannot vanish.
  At the origin both components are zero.
- The only positive root of $\dot r = 0$ is $r = \rho$. As
  polynomials, $r(\rho^2-r^2) = r(\rho-r)(\rho+r)$ (block
  `radial_speed`).
- On the circle $r = \rho$ one has $\dot r = 0$ and
  $\dot\theta = -1 \ne 0$, so the orbit is periodic of period
  $2\pi$.
- On $(0,\rho)$ one has $\dot r > 0$; on $(\rho,\infty)$ one has
  $\dot r < 0$. The circle is invariant, so no orbit crosses it.
  A periodic orbit cannot live in either open annulus, because
  r is strictly monotone there. Hence the circle is the only
  periodic orbit.

The circle is a hyperbolic limit cycle (attracting from both
sides). That is more than uniqueness; uniqueness is the claim.

This is an upper bound of 1 for one documented family, not an
upper bound for all cubics. It does not touch the published
record H(3) at least 13.

## Kept — quadratic Hamiltonian fields, zero limit cycles

Let H be a real polynomial of degree at most 3, and set

$$\dot x = \partial H/\partial y,\qquad
\dot y = -\partial H/\partial x.$$

The field has degree at most 2. Formal differentiation in the
ring of polynomials in x, y and the cubic coefficients of H gives

$$\frac{dH}{dt}
= \frac{\partial H}{\partial x}\frac{\partial H}{\partial y}
+ \frac{\partial H}{\partial y}\Bigl(-\frac{\partial H}{\partial x}\Bigr)
= 0$$

identically (certificate block `hamiltonian`, `dHdt` empty). Every
orbit lies in a level of H.

A periodic orbit cannot contain an equilibrium, so the gradient
of H has no zero on it: the field is exactly the Hamiltonian
rotation of that gradient. A regular compact connected component
of a level of H in the plane is a simple closed curve, and nearby
regular levels supply a continuum of nearby periodic orbits. The
orbit is therefore not isolated, hence not a limit cycle.

The family has periodic orbits (any nondegenerate quadratic
center), but no limit cycles. Zero is sharp as an upper bound on
the number of limit cycles.

## Kept — Lotka–Volterra in the open first quadrant

The quadratic Kolmogorov field

$$\dot x = x(a+bx+cy),\qquad \dot y = y(d+ex+fy)$$

has no limit cycle in the open first quadrant. The proof is a
Dulac identity plus a parallel reduction, not a citation.

Write $B = x^{\alpha-1} y^{\beta-1}$. The normalised divergence

$$\frac{\mathrm{div}(BX)}{B}
= (\alpha-1)\frac{P}{x}+\frac{\partial P}{\partial x}
+ (\beta-1)\frac{Q}{y}+\frac{\partial Q}{\partial y}$$

is the polynomial (block `lotka_volterra`)

$$(\alpha a+\beta d)
+ \bigl((\alpha+1)b+\beta e\bigr)x
+ \bigl(\alpha c+(\beta+1)f\bigr)y.$$

When $\Delta = bf-ce \ne 0$, Cramer's numerators
$\alpha\Delta = f(e-b)$ and $\beta\Delta = b(c-f)$ kill the
coefficients of x and y (block `cramer`, both products are the
zero polynomial). The remaining constant is $K = \alpha a+\beta d$.
If K is nonzero, Bendixson–Dulac says there is no closed orbit in
the first quadrant. If K is zero, BX is divergence-free, hence
locally Hamiltonian, and periodic orbits lie in levels of a first
integral, so they are not isolated.

When Delta is zero the linear parts are parallel. If (b, c) is
zero then $\dot x = ax$: either x is exponential (not periodic)
or a is zero and motion is vertical, hence one-dimensional. The
case (e, f) zero is symmetric. If (e, f) equals lambda times
(b, c), the identity (block `parallel`)

$$\lambda(a+bx+cy)-(d+ex+fy)=\lambda a-d$$

says that lambda log x minus log y has constant derivative
lambda a minus d. If that constant is nonzero the function is
strictly monotone and there is no closed orbit. If it is zero,
$y/x^{\lambda}$ is a first integral and motion on each power
curve is one-dimensional.

In every case there is no isolated periodic orbit in the open
first quadrant. A conservative Volterra center has a continuum
of cycles; those are not limit cycles.

## Dropped / forked

Nothing dropped. No fork. Lean was not added: the identities are
short polynomial cancellations, and a mathlib `ring` lemma would
repeat the Python/Rust check after a long lake fetch.

## What this is not

Not a bound on H(3). Not a bound on H(2). Not a new published
record. The uniqueness lemma is reusable: a stranger can replay
`run.sh` and read the two polar identities off the JSON.

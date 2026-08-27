# Line RR — cubic Kolmogorov, seven cycles

Status: imagined seven-cycle certificate dropped. Fork kept. Not a
dent of `H(3)`. Not a beat of the published Kolmogorov local
cyclicity, and not a claim of the printed Kolmogorov number 28.

Imagined: an explicit cubic Kolmogorov field

$$\dot x=x(a+bx+cy+dx^2+exy+fy^2),\qquad
\dot y=y(g+hx+iy+jx^2+kxy+my^2)$$

has seven isolated periodic orbits in the open first quadrant,
beating Carvalho–Cruz–Gouveia’s local cyclicity

$$\mathcal{M}_K(3)\ge 6$$

or the Gasull–Santana print

$$\mathcal{H}_K(5)\ge 28.$$

Drop immediately. No seven-cycle field is written. The local
record 6 is already on arXiv:2304.05111 (and on Lloyd–Pearson–
Sáez–Szántó 2002 before that). The print 28 is already on
arXiv:2510.11705v2 and is the lift

$$\mathcal{H}_K(n)\ge\mathcal{H}(n-1)$$

applied to the unreplayed seed `H(4) ≥ 28`. Do not claim it
here. Zero cycles in one named cubic family is not a lower
bound, and it does not move `H(n)`.

Fork kept. The axes of a Kolmogorov field are invariant. The
named cubic family below admits a weighted Dulac factor whose
normalised divergence is the constant −1, so Bendixson–Dulac
gives no closed orbit in the open first quadrant. That is an
exact upper bound of 0 isolated cycles for this family, not a
bound on `H(3)` and not a bound on the Kolmogorov numbers.

Replay:

```
problems/hilbert16-limit-cycles/compute/q3/rr-kolmogorov/run.sh
```

Python expands the identities sparsely; Rust expands them
again and evaluates the residuals on an integer box. The two
dumps are `diff`ed. Exit 0. Cert: `certs/identities.json`.
Exact rationals; no floats.

Opened this session: the abs and HTML of Carvalho–Cruz–Gouveia,
arXiv:2304.05111v1; the abs and HTML of Gasull–Santana,
arXiv:2510.11705v2; the abs of Cruz–Oliveira–Torregrosa,
arXiv:2509.06198v1.

## Dropped — seven isolated cycles

The fiction needs an explicit cubic Kolmogorov field with seven
isolated orbits in `x > 0`, `y > 0`. Smooth quadratic
Kolmogorov fields have none (Bautin; restated on
arXiv:2509.06198). q1 already certified that for classical
Lotka–Volterra. A cubic term can create cycles — Lloyd wrote
six, and Carvalho–Cruz–Gouveia give another cubic with local
cyclicity at least 6 — but this line does not write a seventh,
does not unfold a weak focus of order 7, and does not exhibit
a large cycle around the axes-and-infinity graphic.

The printed Kolmogorov number 28 is a different `n` and a
different function: it is `H_K(5)`, not `H(5)`, and it uses
Prohens–Torregrosa’s unreplayed `H(4) ≥ 28`. Citing it as
found here would be a lie.

## Kept — axes invariant

A planar Kolmogorov field is

$$\dot x=x\,p(x,y),\qquad \dot y=y\,q(x,y)$$

with `p`, `q` polynomials. Then `P(0, y) = 0` and
`Q(x, 0) = 0` identically (certificate block `axes`). The
coordinate axes are invariant. Motion on each axis is
one-dimensional, so a periodic orbit of the planar field
cannot live on an axis. The claim below is only about the
open first quadrant.

## Kept — named cubic family, weighted Dulac, zero cycles

Named family, still Kolmogorov, two invariant axes: for every
real `b` and every real `c`,

$$\dot x=x(1-x-y),\qquad
\dot y=y(1-bx-y-c x^2).$$

This is competitive Lotka–Volterra with unit competition on
the first growth rate, plus one cubic term `−c x^2 y` in the
second component. If `c ≠ 0` the field has degree 3. If
`c = 0` it is the q1 Lotka–Volterra slice with growth rates
`(1, −1, −1)` and `(1, −b, −1)`, already known to have no
cycle in the open first quadrant. The cubic term is the
one-degree upgrade.

Write `B = x^{\alpha-1} y^{\beta-1}` and

$$D=\frac{\mathrm{div}(BX)}{B}
=(\alpha-1)p+\partial_x P+(\beta-1)q+\partial_y Q.$$

For the three-parameter parent

$$\dot x=x(1-x-ay),\qquad
\dot y=y(1-bx-y-c x^2)$$

the same formula is the polynomial identity (block
`general`)

$$D=(\alpha+\beta)-(\alpha+1+\beta b)x-(\alpha a+\beta+1)y-\beta c\,x^2.$$

On the named slice `a = 1`, the weights `α = −1` and
`β = 0` kill every non-constant term: `D ≡ −1` (block
`named`). Equivalently, the cleared numerator

$$x\,\partial_x p-p+y\,\partial_y q$$

equals `−1` (block `cleared`). The Dulac function is
`B = x^{-2} y^{-1}`, which is `C^1` and nowhere zero for
`x > 0`, `y > 0`. Then

$$\mathrm{div}(BX)=-x^{-2} y^{-1}<0$$

and is not identically zero on any open set. The open first
quadrant is simply connected, so Bendixson–Dulac says there
is no closed orbit there. In particular there are no isolated
periodic orbits.

The same weights on the parent family give
`D = −1 − (1 − a)y`. That expression is one-signed for
`y > 0` whenever `a ≤ 1`. The official kept statement is the
slice `a = 1`, where the sign is the constant `−1` and no
inequality on `a` is required.

Because `D` is a nonzero constant, `BX` is not
divergence-free: there is no first integral of this weighted
type, and there is no continuum of cycles to discard. The
count is zero, isolated or not.

This is not a bound on `H(3)`. Other cubic Kolmogorov fields
(Lloyd; Carvalho–Cruz–Gouveia) do have cycles. The named
family is a restriction, not a bound on the Kolmogorov
numbers.

## What this is not

Not seven cycles. Not a beat of the published local
cyclicity 6 in degree 3. Not a claim of the printed
Kolmogorov number 28. Not a bound on `H(n)`. A stranger
can run `run.sh` and read the constant −1 and the cycle
count 0 off the dump.

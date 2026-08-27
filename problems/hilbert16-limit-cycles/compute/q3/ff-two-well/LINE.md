# Line FF — two-well cubic Hamiltonian, 14 Abelian zeros

Status: imagined 14-zero certificate dropped. Fork kept. Not a
dent of `H(3)`.

Imagined certificate. The cubic Hamiltonian field of

$$H=\frac{y^2}{2}+\frac{(x^2-1)^2}{4}$$

perturbed by an explicit cubic, has 14 isolated zeros of the
first Abelian integral `I(h)` across the two small wells and
the large annulus, hence `H(3) ≥ 14` without Li–Liu–Yang.

Drop immediately. No 14-zero integral is written. The first
Melnikov function of the named cubic perturbation is an
elliptic integral on each nest; one exact sample is nonzero
and the 3-jet Lyapunov quantity at each well is a nonzero
multiple of `μ`. That proves `I` is not identically zero. It
does not produce 14 zeros, and it does not beat
Li–Liu–Yang `H(3) ≥ 13`.

Fork kept. The unperturbed field, the energy identities, the
formula for `I(h)`, the exact value of `I` on each lobe of
the figure-eight, and the exact first Lyapunov quantity at
each well after translation to the q1 focal form. Symbolic
only; no ODE integration. Fractions as strings. Not a bound
on `H(n)`.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/ff-two-well/run.sh
```

Python expands the identities sparsely; Rust expands them
again and evaluates the cleared `dH/dt` residuals on the
integer box from −3 to 3. The two dumps are `diff`ed. Exit 0.
Certs: `certs/core.json`, `certs/identities.json`.

## Dropped — fourteen zeros of I(h), hence H(3) at least 14

The fiction needs an explicit cubic perturbation whose
Abelian integral has 14 isolated zeros on the three period
annuli (two nests and the outer well). Picard–Fuchs dimension
for this Hamiltonian is small; typical first-order counts are
a handful, not 14. Harnack still caps one invariant cubic at
two ovals. No closed form of `I(h)` with 14 roots is
produced, and a numeric search of an elliptic integral is
not a lower bound.

The named perturbation below is degree 3, so it is the right
degree. The integral is written. The 14 roots are not.

## Kept — unperturbed two-well field

The field is

$$\dot x=y,\qquad \dot y=x-x^3.$$

It is Hamiltonian for

$$H=\frac{y^2}{2}+\frac{x^4}{4}-\frac{x^2}{2},$$

which is the user’s double well shifted by a constant:

$$\frac{y^2}{2}+\frac{(x^2-1)^2}{4}=H+\frac{1}{4}.$$

The certificate uses the cleared polynomial
`H4 = 4H = 2y² + x⁴ − 2x²`, so every identity stays in
`Z[x, y]`. Formal differentiation gives `dH4/dt ≡ 0`
(block `unperturbed`). Divergence vanishes identically.

Equilibria of `(y, x − x³)`: `y = 0` and `x(1 − x²) = 0`,
hence `(0, 0)` and `(±1, 0)`. The Jacobian is

$$\begin{pmatrix}0&1\\1-3x^2&0\end{pmatrix},$$

trace 0 everywhere, determinant `3x² − 1`. At `(0, 0)` the
determinant is `−1` (saddle). At `(±1, 0)` it is `2`
(linear centers, frequency `√2`). Energy: `H(0, 0) = 0` and
`H(±1, 0) = −1/4`. The figure-eight through the saddle is
the level `H = 0`. Each nest oval lives in
`H ∈ (−1/4, 0)`.

## Kept — named cubic perturbation and I(h)

Perturb by van der Pol damping on the same wells,

$$\dot x=y,\qquad \dot y=x-x^3+\mu(1-x^2)y.$$

Still degree 3. Along the perturbation,

$$\frac{dH}{dt}=\mu\, y^2(1-x^2)$$

(block `perturbed`; equivalently `dH4/dt = 4μ y² (1 − x²)`).
Energy increases where `|x| < 1` and decreases where
`|x| > 1`. The first Melnikov function on a level `H = h` is

$$I(h)=\oint_{H=h}\mu(1-x^2)\,y\,dx,$$

or, on a nest oval with `y = ±√(2h − x⁴/2 + x²)`,

$$I(h)=2\mu\int_{x_{\min}}^{x_{\max}}(1-x^2)\sqrt{2h-\tfrac{1}{2}x^4+x^2}\,dx.$$

No elementary antiderivative in the open wells is claimed.
Two exact samples are.

At the bottom of each well the oval shrinks to a point and
`I(−1/4) = 0`. On the figure-eight `H = 0`, each lobe is
elementary. The right lobe has `x ∈ [0, √2]` and

$$\sqrt{x^2-\tfrac{1}{2}x^4}=|x|\sqrt{1-\tfrac{1}{2}x^2}.$$

The substitutions `u = x²` then `w = 1 − u/2` then
`t = √w` reduce the integral to

$$\int_0^1(4t^4-2t^2)\,dt=\Bigl[\tfrac{4}{5}t^5-\tfrac{2}{3}t^3\Bigr]_0^1=\tfrac{4}{5}-\tfrac{2}{3}=\tfrac{2}{15}.$$

Clearing denominators, `15` times the antiderivative is
`12t⁵ − 10t³`, and its derivative minus `15(4t⁴ − 2t²)` is
the zero polynomial (block `figure_eight`). The prefactors
assemble to

$$I_{\mathrm{right}}(0)=\frac{4\mu}{15}.$$

The integrand depends only on `x²`, so the left lobe equals
the right lobe. For `μ ≠ 0` this value is nonzero, so `I` is
not the zero function on either nest (the figure-eight is
the boundary of each nest). Counted isolated zeros of `I` on
regular ovals: none exhibited. The figure-eight itself does
not persist at first order.

## Kept — L1 at both wells

Translate each unperturbed center to the origin and put the
3-jet in the q1 focal form

$$\dot u=-v+a_{20}u^2+\cdots,\qquad
\dot v=u+b_{20}u^2+\cdots.$$

The linear part at `(±1, 0)` is `Ẋ = Y`, `Ẏ = −2X`. The
change `u = X`, `v = −Y/√2`, `τ = √2 t` (so `s² = 2` with
`s = √2`) normalises the frequency to 1. After that change
the 1-component of the field is exactly `−v`. The
2-component is recorded in the certificate (block `jets`).

The q1 primitive, written for quadratic fields, is

$$L_1^{\mathrm{quad}}=(a_{20}+a_{02})a_{11}-(b_{20}+b_{02})b_{11}-2a_{20}b_{20}+2a_{02}b_{02}.$$

The same Poincaré–Lyapunov calculation as q1, carried
through the 3-jet, extends it by the unique cubic correction
that keeps `V_1 = L_1/8`:

$$L_1=L_1^{\mathrm{quad}}+3a_{30}+a_{12}+b_{21}+3b_{03}.$$

At `x = 1`, after the scaling,

`b20 = 3/2`, `b11 = −√2 μ`, `b30 = 1/2`,
`b21 = −√2 μ / 2`, and every `a_{ij} = 0`. Then

$$L_1^{\mathrm{quad}}=\frac{3\sqrt{2}}{2}\,\mu,\qquad
3a_{30}+a_{12}+b_{21}+3b_{03}=-\frac{\sqrt{2}}{2}\,\mu,$$

$$L_1=\sqrt{2}\,\mu,\qquad V_1=\frac{\sqrt{2}\,\mu}{8}.$$

At `x = −1` the quadratic jet flips sign
(`b20 = −3/2`, `b11 = √2 μ`) and the same two pieces
reassemble to the same `L_1 = √2 μ`. When `μ = 0` both
pieces cancel and `L_1 = 0`, as they must: the unperturbed
equilibria are centers.

The perturbation does not move the linearization at the
wells: `∂Q/∂y = μ(1 − x²)` vanishes at `x = ±1`, so the
trace stays 0 and the determinant stays 2. For `μ ≠ 0` each
well is a weak focus of order 1, not a linear focus. The
cubic displacement in q1 gauge is
`a3(2π) = (π/4) L_1 = (π/4) √2 μ`. That return map, at
this order, vanishes only at radius 0. A Hopf birth of a
small cycle needs a trace unfolding, which this family does
not have at `(±1, 0)`. Two small cycles are not proved and
are not claimed. Two Hopf cycles would not beat
`H(3) ≥ 13` in any case.

The saddle stays a saddle. At `(0, 0)` the perturbed
Jacobian is `[[0, 1], [1, μ]]`, determinant `−1`, trace `μ`.
The characteristic polynomial is `λ² − μλ − 1`. Determinant
negative for every real `μ`.

## What this is not

Not a bound on `H(n)`. Not a dent. Not fourteen zeros of an
Abelian integral. Not a proved pair of limit cycles. The
identities are reusable: a stranger can run `run.sh` and
read `L1 = √2 μ` and `I(0) = 4μ/15` off the JSON.

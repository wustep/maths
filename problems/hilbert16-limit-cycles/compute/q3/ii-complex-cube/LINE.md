# Line II — holomorphic cube

Status: 9-sheet claim dropped. Kept: Cauchy–Riemann, Jacobian,
generic fibre of 3, pullback degree N = 3n+2, and the comparison
that T3 is strictly stronger at the same N. H(n) did not move.

Imagined: the holomorphic cube
Φ = (u³ − 3uv², 3u²v − v³) (that is z ↦ z³) is 9-to-1, so the
Remark 4 pullback multiplies cycles by 9 and matches Chebyshev
T3 without being separable.

Dropped: Cauchy–Riemann makes the real map 3-to-1, not 9-to-1.
The degree is the same as T3, N = 3n+2, but the sheet count is
3 = (N+1)/(n+1), linear. Bézout still allows 9. T3 attains those
9. The holomorphic cube is strictly weaker.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/ii-complex-cube/run.sh
```

Python expands the identities over Q; rustc expands them again
with a BTreeMap of monomials, a 5×5 Sylvester resultant, and
polar cube roots. The two dumps are `diff`ed. Exit 0.

Opened this session:
[arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883) and its
[HTML](https://arxiv.org/html/2604.12883v1) (Theorem 1, Theorem 2,
Remark 4, §6 cubic).

## Dropped — nine regular sheets from the cube

The imagined certificate was that

$$\Phi(u,v)=(u^3-3uv^2,\,3u^2v-v^3)$$

is 9-to-1 on the real plane, so the Remark 4 pullback of the
radial cubic of q1 line D / 2604.12883 §6 would produce nine
hyperbolic cycles in degree 11, matching T3 without being
separable.

That does not happen. As a real plane map, z ↦ z³ is 3-to-1
away from the origin, not 9-to-1. The two components are tied
by the Cauchy–Riemann equations, so the Bézout number m² = 9
per degree-3 step is not attained. The actual regular-sheet
count is 3, which is linear in the degree:

$$N=3n+2,\qquad 3=\frac{N+1}{n+1}.$$

Separable T3 has the same N and attains 9.

## Kept — CR, fibre 3, degree 3n+2, weaker than T3

Write the components Φ = u³ − 3uv² and Ψ = 3u²v − v³ of the
cube map. The partials are the identities

$$\Phi_u=3(u^2-v^2),\quad \Phi_v=-6uv,\quad \Psi_u=6uv,\quad \Psi_v=3(u^2-v^2),$$

together with Cauchy–Riemann (the first equals the fourth, the
second is minus the third). The Jacobian is

$$\det D\Phi=\Phi_u\Psi_v-\Phi_v\Psi_u=\Phi_u^2+\Phi_v^2=9(u^2+v^2)^2\ge 0,$$

vanishing only at the origin. The modulus identity
Φ² + Ψ² = (u² + v²)³ is |z³|² = |z|⁶.

Generic fibre. For (x, y) ≠ 0 the equation z³ = x + iy has
three solutions in R² ≅ C. Polar: a unique radius
r = (x² + y²)^{1/6} and three arguments
θ = (arg(x+iy) + 2πk)/3, k = 0, 1, 2. Resultant of
u³ − 3uv² − x and 3u²v − v³ − y with respect to v is

$$64u^9-48xu^6-15x^2u^3-27y^2u^3-x^3,$$

a cubic in t = u³ (Bézout 9 over C, after the three cube
roots of t). Regular real preimages of (1/2, 0) and of
(1/4, 1/4) are 3, not 9. The same target (1/2, 1/2) under
separable T3 × T3 has 9, attaining m².

Degree of the pullback. The Remark 4 field is
Y = adj(DΦ)(X ∘ Φ),

$$\dot u=\Psi_v\,P(\Phi)-\Phi_v\,Q(\Phi),\qquad
\dot v=-\Psi_u\,P(\Phi)+\Phi_u\,Q(\Phi),$$

so that DΦ · Y = (det DΦ)(X ∘ Φ). The Jacobian cofactors have
degree 2 and X ∘ Φ has degree 3n, hence

$$\deg Y=n\cdot 3+2=3n+2.$$

Checked: n = 1 (linear centre) gives exact degree 5, closed
form Ẏ = (3v(u²+v²)², −3u(u²+v²)²); n = 2 (the sample
(x² + y, y² + x)) gives exact degree 8; n = 3 (radial cubic
with ρ² = 1/4) gives exact degree 11, with 12 + 12 monomials
and leading part −3(u, v)(u² + v²)⁵. One-step T3 of the
same three fields has the same degrees 5, 8, 11.

Sheets. If every cycle of a degree-n field lifted through
all three regular preimages,

$$3\,H(n)\le H(3n+2).$$

Chebyshev T3 has m = 3 and the same degree budget
N = n · 3 + 3 − 1 = 3n+2, and claims

$$9\,H(n)\le H(3n+2).$$

Same N. The holomorphic cube only contributes 3. Strictly
weaker than the paper's T3 at the same N. Bézout still
allows 9 = ((N+1)/(n+1))², quadratic in the 3; T3 attains
that ceiling and the cube does not.

Remark 4 of 2604.12883 asked whether a non-separable
covering could change the replication rate. For this
holomorphic map the answer is negative: an analogue of
Theorem 2 still holds, and the growth is strictly slower
than the separable ceiling at the same degree.

The radial cubic of q1 §6,

$$\dot x=y-x(x^2+y^2-1/4),\qquad\dot y=-x-y(x^2+y^2-1/4),$$

pulls back to an explicit degree-11 field (12 + 12 terms).
Even if its one hyperbolic circle lifted three ways, that
would be H(11) ≥ 3, which loses to T3's H(11) ≥ 9 and to
Han–Li 153.

## Certificates

All checks are in `certs/` and in the dump that `run.sh`
diffs.

1. CR and Jacobian on Φ = (u³ − 3uv², 3u²v − v³). Residuals
   of the adj identity are the zero polynomial for the
   linear centre, the sample quadratic, and the radial
   cubic. det DΦ = 9(u² + v²)². Modulus identity holds.
2. Degrees: n = 1 → N = 5; n = 2 → N = 8; n = 3 → N = 11,
   all exact. T3 one-step of the same three fields matches
   those degrees. Radial Yu, Yv have 12 monomials each.
3. Regular real preimages of (1/2, 0) and of (1/4, 1/4):
   3, not 9. Complex affine count 9 (Bézout). T3 × T3 of
   (1/2, 1/2) has 9. Resultant is degree 9 in u and degree
   3 in u³. Polar cube roots of both targets give three
   distinct regular preimages.
4. Arithmetic, n = 1, 2, 3:

| n | N | cube sheets | Bézout 9 | T3 sheets | (N+1)/(n+1) |
|---|---|-------------|----------|-----------|-------------|
| 1 | 5 | 3 | 9 | 9 | 3 |
| 2 | 8 | 3 | 9 | 9 | 3 |
| 3 | 11 | 3 | 9 | 9 | 3 |

## What this is not

Not a bound on H(n). Not a new seed. Even if each regular
sheet lifted one hyperbolic cycle of the radial cubic, the
count would be 3 in degree 11, which does not beat a
published row and loses to the paper's own T3 lift. Do not
cite 252, 1080, 1380, or 2012 as found here. Theorem 1 of
2604.12883 is not improved; this line only says that this
particular holomorphic cube does not attain the Bézout
ceiling and is strictly weaker than T3 at the same N.

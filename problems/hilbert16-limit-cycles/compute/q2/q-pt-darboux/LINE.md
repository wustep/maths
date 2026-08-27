# Line Q — Prohens–Torregrosa seed and Coppel contacts

Status: 29 dropped. Seed and contact identities kept. Not a dent of
H(4).

The imagined extra Hopf cycle is not a finite identity we can
write. The unperturbed Darboux field, and the quadratic
contact/collinearity identities that sit under Coppel's Theorem 2,
are.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q2/q-pt-darboux/run.sh
```

Python expands the Darboux field with sympy and the contact
identities in the same ring. Rust expands the same polynomials
with a BTreeMap and a Sylvester determinant, and also evaluates
the cleared dH/dt numerator on the integer box from -6 to 6 in
each variable. A degree-at-most-12 polynomial in two variables
that vanishes on that box is zero. The two dumps are `diff`ed.
Exit 0.

Opened this session: the UAB copy of Prohens–Torregrosa,
Nonlinearity 32 (2019), Proposition 6 and system (20);
Coppel 1966 Theorems 1–2 as logged in RESEARCH.md.

## Dropped — H(4) at least 29

Proposition 6 of Prohens–Torregrosa associates a degree-4 field
to the rational first integral

$$H = \frac{(2x^4-x^2+y^2-2x-2)^5}{(8x^5-5x^3+5xy^2-10x^2-5x-4)^4}$$

and, after a degree-4 perturbation, quotes the configurations
⟨6, 10, 6⟩, ⟨8, 11, 8⟩, and ⟨8, 12, 8⟩ from Lyapunov orders 1, 3,
and 5. The order-5 budget is already 28. A 29th cycle would need
one more independent quantity at the middle focus. They stopped
at 28. No explicit 28-cycle perturbation is written term-by-term
on the page. This line does not invent that field, and it does
not add a 29th cycle.

## Kept — unperturbed Darboux field

Write A = 2x⁴ − x² + y² − 2x − 2 and
B = 8x⁵ − 5x³ + 5x y² − 10x² − 5x − 4. The standard polynomial
field with first integral H = A⁵ / B⁴ is

$$P = -5 B A_y + 4 A B_y,\qquad
Q = 5 B A_x - 4 A B_x.$$

The partials are

$$A_y=2y,\quad B_y=10xy,\quad
A_x=8x^3-2x-2,\quad
B_x=40x^4-15x^2+5y^2-20x-5.$$

Then

$$P = 10y(-B + 4x A).$$

The combination −B + 4x A cancels in degree 5 and is the cubic
x³ + 2x² − x y² − 3x + 4 (certificate block `inner`). So P has
degree 4. The same expansion gives Q of degree 4. Both components
share the integer content 10 and no non-constant common factor.
The primitive field (block `darboux`) is

$$\dot x = y(x^3 + 2x^2 - xy^2 - 3x + 4),$$

$$\dot y = 15x^4 - 21x^3 + 3x^2 y^2 - 15x^2 + 7x y^2 - 11x - 2y^4 + 6y^2.$$

Exact checks, none of which is a numerical ODE:

- max(deg P, deg Q) = 4 after cancelling the content.
- The points (0, 0), (1, 2), and (1, −2) are equilibria.
- The Jacobian at (0, 0) is [[0, 4], [−11, 0]]: trace 0, det 44.
  At (1, ±2) it is [[0, −8], [8, 0]]: trace 0, det 64. Each
  linearization is a center.
- Clearing the denominator of dH/dt leaves the numerator

  $$(5BA_x-4AB_x)P+(5BA_y-4AB_y)Q,$$

  which is the zero polynomial (block `dHdt_numer` empty). Regular
  compact levels of H are continua of periodic orbits, so the
  unperturbed field has no limit cycles.

## Kept — cubic system (20), not a dent of H(3)

The same paper writes the cubic

$$\dot x = y^3 - y,\qquad \dot y = -8x^3 - 3x^2 + x$$

with polynomial first integral
H = −8x⁴ − y⁴ − 4x³ + 2x² + 2y². That field is a constant
multiple of the Hamiltonian field of H, so dH/dt vanishes
identically (block `cubic20`). The origin is a linear center
(trace 0, det 1). Nearby regular levels are not isolated. This
is not a dent of H(3), and it does not beat Li–Liu–Yang 13.

On the line y = 0 one has P ≡ 0 and
Q(t, 0) = −t(8t² + 3t − 1). The quadratic 8t² + 3t − 1 has
discriminant 41 > 0 and nonzero constant term, so three distinct
real roots. A cubic may have three collinear finite equilibria.
The degree-2 restriction below is what stops that for quadratics.

## Kept — Coppel contact and collinearity identities

Coppel 1966, Theorem 2, says a closed path of a real quadratic
field surrounds a unique critical point. The facts underneath,
as polynomial identities, are these. We do not claim the rest of
that paper (convexity of interiors, orientation of nests, the
focus-or-center type of the interior point).

On the affine line y = 0 a general quadratic

$$\dot x = a_{00}+a_{10}x+a_{01}y+a_{20}x^2+a_{11}xy+a_{02}y^2,$$

$$\dot y = b_{00}+b_{10}x+b_{01}y+b_{20}x^2+b_{11}xy+b_{02}y^2$$

restricts to the univariates P(t, 0) = a00 + a10 t + a20 t² and
Q(t, 0) = b00 + b10 t + b20 t², each of degree at most 2
(block `line`). Contacts or equilibria on y = 0 are among the
zeros of Q(t, 0), because the line is horizontal. A nonzero
univariate of degree at most 2 has at most two roots, so a line
that is not filled with equilibria meets the field in at most
two contacts-or-equilibria.

If both restrictions vanish at three distinct points t1, t2, t3,
both are the zero polynomial. The 3×3 Vandermonde matrix V with
rows (1, ti, ti²) has

$$\det V = -(t_1-t_2)(t_1-t_3)(t_2-t_3),$$

and adj(V) V − (det V) I is the zero matrix (block
`vandermonde`). Hence three collinear finite equilibria of a
quadratic force P and Q to vanish identically on that line: the
line is filled with equilibria and cannot cut a closed orbit in
the isolated-contact way.

A closed orbit cannot contain two isolated finite equilibria in
its interior for the same reason, once one grants Coppel's
Theorem 1 (the interior is convex) and that a line meets a
quadratic orbit in at most two points. The segment between the
two equilibria would lie in the interior, and the line through
them would then carry two equilibria plus two extra intersections
with the cycle, four zeros of a degree-at-most-2 contact
polynomial. This line certifies the degree bound and the
three-implies-identically-zero identity, not the convexity.

Sample: the unperturbed Shi field of q1,

$$\dot x = -y-10x^2+5xy+y^2,\qquad \dot y = x+x^2-25xy,$$

has resultant Res_y(P, Q) = −6124 x⁴ + 102 x³ − 24 x²
(block `shi`). That factors as −2x²(3062 x² − 51 x + 12); the
quadratic 6124 x² − 102 x + 24 has discriminant −577500 < 0, so
the only real finite equilibria are the two points with x = 0,
namely (0, 0) and (0, 1). There is no third real finite
equilibrium to be collinear with them.

For a generic quadratic the same Sylvester resultant Res_y(P, Q)
is a polynomial of degree at most 4 in x (block `resultant`,
63 monomials, leading form of degree 4). Bézout allows at most
four finite intersections, counting multiplicity and points at
infinity.

## What this is not

Not a bound on H(4). Not a bound on H(2). Not a replay of the
⟨8, 12, 8⟩ Lyapunov budget, and not a proof of Coppel's
theorems. The lemmas that are reusable are the primitive
Darboux field and the two contact identities: a stranger can
run `run.sh` and read both off the JSON.

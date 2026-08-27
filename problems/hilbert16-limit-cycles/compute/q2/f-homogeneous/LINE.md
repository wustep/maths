# Line F — homogeneous / quasi-homogeneous isolated cycles

Status: imagined certificate dropped. Fork kept. Not a dent of
`H(n)`.

Imagined certificate. A homogeneous planar field of degree
n ≥ 2 has n isolated periodic orbits. Polar identities
ṙ = r^n f(θ), θ̇ = r^{n-1} g(θ) were supposed to produce n
simple zeros of f on the circle, each a cycle.

Drop immediately. Homogeneous fields are scaling-equivariant:
(x, y, t) ↦ (λx, λy, λ^{1-n} t). A compact periodic orbit
Γ ⊂ R² \ {0} scales to a distinct periodic orbit λΓ for
λ ≠ 1, hence a continuum. Quasi-homogeneous weights (s1, s2)
and weighted degree d give
(x, y, t) ↦ (λ^{s1} x, λ^{s2} y, λ^{1-d} t), same argument.
Polar form is the checkable identity, not a numeric search.
Zeros of f are not cycles.

Fork kept. Unperturbed homogeneous polynomial fields, and
unperturbed quasi-homogeneous centers, have zero isolated
periodic orbits. Exact polar / weighted-polar identities in
Z, Python and a second language. Not a bound on H(n).

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q2/f-homogeneous/run.sh
```

Python expands the identities sparsely; Rust expands them
again and evaluates the concrete residuals on an integer box.
The two dumps are `diff`ed. Exit 0.

## Dropped — n isolated cycles

The fiction dies on scaling before any search. If
(x(t), y(t)) solves a degree-n homogeneous field, so does
(λ x(λ^{n-1} t), λ y(λ^{n-1} t)). That is the polynomial
identity P(λx, λy) = λ^n P(x, y) (and the same for Q),
written as an ODE on a concrete cubic in the certificate
block `scale`. A compact orbit missing the origin is sent
to a distinct compact orbit. Isolated periodic orbits cannot
occur.

The polar rewrite does not rescue the fiction. For
homogeneous P, Q of degree n,

xP + yQ is homogeneous of degree n + 1, and
xQ − yP is homogeneous of degree n + 1.

Those are the identities
F(λx, λy) − λ^{n+1} F ≡ 0 and
G(λx, λy) − λ^{n+1} G ≡ 0
in Z[x, y, λ, coefficients], certified for generic n = 2
and n = 3 (blocks `homog2`, `homog3`). Clearing the radius
gives ṙ = r^n f(θ) and θ̇ = r^{n-1} g(θ) with no
trigonometric expansion. Isolated zeros of f are not
periodic orbits. Isolated zeros of g are invariant rays.

## Kept — unperturbed homogeneous fields, zero isolated cycles

Two exhaustive pictures, both algebraic.

If F = xP + yQ vanishes identically and G = xQ − yP does
not, every circle about the origin is invariant. The cubic
example P = −y(x² + y²), Q = x(x² + y²) has F ≡ 0 and
G = (x² + y²)² (block `circles`). Off the origin,
θ̇ = r² ≠ 0, so every circle is periodic. A continuum; zero
isolated cycles.

If F is not identically zero, there is no invariant circle
about the origin. The quadratic example P = x², Q = y² has
F = x³ + y³ ≢ 0 and G = xy(y − x) (block `rays`). The three
linear factors of G are invariant rays: on x = 0 the field
is vertical, on y = 0 it is horizontal, on y = x it is
parallel to (1, 1). A ray is not a cycle. The real zeros of
F lie on the line x + y = 0; the field is not tangent to
that line (normal component 2x² ≢ 0), so a zero of f need
not even be a ray.

In every homogeneous case the scaling identity already
forbids an isolated compact orbit in R² \ {0}. The origin
is an equilibrium and is not a periodic orbit.

## Kept — unperturbed quasi-homogeneous center, zero isolated cycles

The field ẋ = 2y, ẏ = −x³ is Hamiltonian for
H = x⁴ + 4y² (equal to 4 times x⁴/4 + y²). Formal
differentiation gives dH/dt ≡ 0 (block `quasihomogeneous`).
Regular levels H = c > 0 are compact ovals: H vanishes only
at the origin, and ∇H vanishes only there. Each oval is a
periodic orbit. A continuum; zero isolated cycles.

The same field is quasi-homogeneous of weighted degree 2
for weights (s1, s2) = (1, 2):

P(λx, λ²y) = λ² P, Q(λx, λ²y) = λ³ Q,
H(λx, λ²y) = λ⁴ H.

The last identity is the period annulus in scaled
coordinates: each level H = c maps to the distinct level
H = λ⁴ c. Same conclusion as the homogeneous scaling
argument. This is the unperturbed half of imagined J, not
a Melnikov count and not a bound on H(n).

## What this is not

Not a bound on H(n). Not a dent. A homogeneous or
unperturbed quasi-homogeneous field is the wrong family
for isolated cycles; the identities show there are none.
Perturbations of the quasi-homogeneous center are a
different problem and are not certified here.

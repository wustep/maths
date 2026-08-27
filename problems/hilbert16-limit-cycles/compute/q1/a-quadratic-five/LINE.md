# A — quadratic five

Imagined: there is an explicit quadratic planar field, a
perturbation of Shi Songling 1980,

    dx/dt = λx − y − 10 x² + (5+δ) x y + y²
    dy/dt = x + x² + (−25 + 8ε − 9δ) x y + μ y²

with five isolated periodic orbits, hence H(2) ≥ 5.

Dropped the five-cycle claim. Forked to an exact certificate on
the unperturbed field (λ = ε = δ = μ = 0). Published H(n) moved?
no.

Replay:

```
problems/hilbert16-limit-cycles/compute/q1/a-quadratic-five/run.sh
```

## Exact statement (replayed)

The unperturbed Shi field

    dx/dt = −y − 10 x² + 5 x y + y²
    dy/dt = x + x² − 25 x y

has a weak focus of order 3 at the origin: the Poincaré–Lyapunov
function F = (x²+y²)/2 + F3 + ⋯ + F8, with the yⁿ coefficient of
each even Fₙ pinned to 0, satisfies

    dF/dt = V3 (x²+y²)⁴ + O(9),    V1 = V2 = 0,    V3 = 35625/8.

Li Chengzhi’s polynomials on the same jet (Llibre–Schlomiuk,
Canad. J. Math. 56 (2004), after Proposition 2) are
L1 = L2 = 0, L3 = 57000 = (64/5) V3. They vanish together.

There are exactly two real finite equilibria (Bézout 4, the other
two complex). The second is (0, 1), a strong unstable focus:
Jacobian [[5, 1], [−24, 0]], characteristic polynomial
t² − 5 t + 24, discriminant −71.

Python builds F and writes `cert.json`. Python then differentiates
F along the field and checks the identity, the Li polynomials, the
resultant/discriminant count, and the Jacobian. C differentiates
the same F from `f_coeffs.txt` over rationals and checks the
degree-≤8 identity again.

## Why five failed

Four small cycles at the origin contradict Bautin (cyclicity ≤ 3
at a quadratic focus).

A fifth cycle surrounding both foci contradicts Coppel: a
quadratic limit cycle surrounds a unique singular point, and that
point is a focus (Llibre–Schlomiuk §7.1(iv), citing Coppel 1966).

The remaining story is (3, 2) or a second large cycle from μ.

μ y² destroys the order-3 jet: the primitive first Lyapunov
quantity at the origin is 27μ, so V1 = 27μ/8. Order 3 requires
μ = 0. When μ ≠ 0 the point (0, 1) is no longer an equilibrium
(Q(0, 1) = μ).

To make (0, 1) itself a weak focus inside the family one needs
trace λ + 5 + δ = 0. The classical small Shi unfolding has
|δ| tiny and trace ≈ 5. The one-parameter try δ = −5, λ = ε = 0
makes Li’s L1 = L2 = L3 all vanish (the origin becomes a center)
and makes det J(0, 1) = −21 < 0 (a saddle, not a focus).

If one forces a focus at (0, 1) with zero trace and a weak origin
(λ = 0, δ = −5, μ = 0, ε < −21/8), the origin is only order 1
(L1 = −8ε ≠ 0). Bautin’s budget is then 1 + 3 = 4, not 5. That
parameter is also not a perturbation of Shi.

Galias–Tucker–Wilczak (AMC 2022) prove the Songling field with
μ = 0 and the classical tiny (δ, ε, λ) has exactly four cycles.
That is one system, not H(2) = 4, and it is not a fifth cycle.

Numerical ODE integration of a guessed (λ, ε, δ, μ) is residue,
not a lower bound. This line does not claim H(2) ≥ 5.

## Annulus

A Poincaré–Bendixson trapping pair for a large cycle about (0, 1)
needs two nested algebraic ovals with definite Lie derivative.
On Euclidean circles about (0, 1),

    d/dt (x²+(y−1)²) = r² (5 + 5 cos 2θ − 23 sin 2θ) + O(r³),

and 5 ± √554 have opposite signs (554 > 25), so those circles
already fail at linear order. Axis-aligned ellipses sampled
afterwards also change sign. No exact trapping pair. Residue.

Opened this session: the Llibre–Schlomiuk 2004 text (Li formulas;
Coppel as §7.1(iv)); the Yu–Zhang and Galias–Tucker–Wilczak PDFs
were fetched (HTTP 200) for the coefficient transcription already
in RESEARCH.md.

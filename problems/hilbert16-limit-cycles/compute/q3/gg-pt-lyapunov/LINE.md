# Line GG — L1 at the three PT Darboux centers

Status: 29 dropped. Unperturbed L1 = 0 at the three centers kept.
Not a dent of H(4).

Imagined certificate. After translating the three reconstructed
centers of the explicit degree-4 Darboux field from q2 to the
origin and putting each quadratic-plus-cubic jet into the q1
normal form, the first Lyapunov quantities together with the
three traces were supposed to give 29 independent conditions,
hence a 29th cycle and H(4) ≥ 29.

Drop immediately. The unperturbed field is a Darboux center:
dH/dt vanishes identically. Every Lyapunov quantity is zero, so
there is no order-1 focus and no extra small cycle from L1 of
the unperturbed jet. Prohens–Torregrosa already ran the
perturbed budget through order 5 and stopped at 28; their
first-order count is 22, not 29. We do not have their
perturbation as an explicit polynomial field, and this line
does not invent one.

The finite check that remains is the vanishing itself, plus
the linearizations already in q2, plus L1(μ) for two
location-preserving perturbations that stay degree 4. Three
Hopf cycles from three centers would be H(4) ≥ 3, useless
against 28.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/gg-pt-lyapunov/run.sh
```

Python expands the jets with sympy and re-derives Poincaré V1
in the same gauge as q1. Rust expands the same field with a
sparse bivariate map and evaluates L1 over Q(√11). The two
dumps are `diff`ed. Exit 0.

## Dropped — H(4) at least 29

A 29th cycle would need an independent quantity beyond the
order-5 Lyapunov budget that already produces ⟨8, 12, 8⟩ = 28
in Prohens–Torregrosa, Nonlinearity 32 (2019), Proposition 6.
The seed we own is the unperturbed Darboux field. At a center,
L1 = L2 = ⋯ = 0. Rank of the unperturbed L1 map is zero, not
29. No explicit 28-cycle perturbation is written term-by-term
in the repo, and this line does not add a 29th cycle.

## Kept — linearizations, replayed from q2

The primitive field (content 10 cancelled) is

$$\dot x = y(x^3+2x^2-xy^2-3x+4),$$

$$\dot y = 15x^4-21x^3+3x^2y^2-15x^2+7xy^2-11x-2y^4+6y^2.$$

The points (0, 0), (1, 2), and (1, −2) are equilibria. The
Jacobian at (0, 0) is [[0, 4], [−11, 0]]: trace 0, det 44.
At (1, ±2) it is [[0, −8], [8, 0]]: trace 0, det 64. Each
linearization is a center. Certificate block `centers`.

## Kept — L1 of the unperturbed jet is zero

The q1 line-E polynomial is the first Lyapunov quantity of a
quadratic jet in the normal form ẋ = −y + ⋯, ẏ = x + ⋯:

$$L1_E=(a_{20}+a_{02})a_{11}-(b_{20}+b_{02})b_{11}-2a_{20}b_{20}+2a_{02}b_{02}.$$

A degree-4 field has a cubic jet after translation. The same
Poincaré function that produced V1 = L1_E / 8 on a quadratic
adds the cubic terms 3 a30 + a12 + b21 + 3 b03, so

$$L1=L1_E+3a_{30}+a_{12}+b_{21}+3b_{03},\qquad V1=L1/8.$$

When the cubics vanish this is the q1 polynomial. Both
languages evaluate L1 after a linear change and a time
rescaling that put the linear part into (−η, ξ). At (0, 0)
that change is over Q(√11); at (1, ±2) it is division by 8.

Unperturbed values (certificate `centers`):

| point | L1_E | cubic piece | L1 |
| --- | --- | --- | --- |
| (0, 0) | 0 | 0 | 0 |
| (1, 2) | 9/2 | −9/2 | 0 |
| (1, −2) | −9/2 | 9/2 | 0 |

Evaluating only L1_E at (1, ±2) would falsely call those
points order-1 foci. The cubic jet cancels L1_E, as it must
for a Darboux center. The three points are not order-1 foci.

## Kept — first jet after linear at the origin

In the original coordinates the terms after the linear part
4y and −11x are the exact integers

$$P_2=-3xy,\quad Q_2=-15x^2+6y^2,$$

$$P_3=2x^2y,\quad Q_3=-21x^3+7xy^2.$$

## Kept — L1(μ) for location-preserving perturbations

These stay degree 4 and keep the three points as equilibria.
They are not a dent of H(4).

The example μ x(x−1)y added to P vanishes on x = 0 and x = 1,
so the three centers stay equilibria. At (0, 0) the trace
stays 0 and L1 stays 0. At (1, ±2) the perturbation produces
linear terms: traces 2μ and −2μ. Those are strong foci when
μ ≠ 0, so L1 is not the first quantity (certificate
`user_xy`).

The perturbation μ x(x−1)² y vanishes at the three points
and has divergence 0 there, so the traces stay 0. Then

$$L1(0,0)=0,\qquad L1(1,2)=-\mu,\qquad L1(1,-2)=\mu.$$

The origin is still not an order-1 focus. The other two
become order-1 weak foci for μ ≠ 0.

The perturbation μ x²(x−1)² added to P likewise preserves
locations and traces, and moves all three:

$$L1(0,0)=-\frac{351\sqrt{11}}{968}\mu,\qquad
L1(1,\pm 2)=-\frac{\mu}{8}.$$

Three small cycles from three order-1 foci would be H(4) ≥ 3.
That does not beat 28. The polynomials are the finite object.

## What this is not

Not a bound on H(4). Not a replay of the ⟨8, 12, 8⟩ Lyapunov
budget. Not an explicit 28-cycle or 29-cycle perturbation.
The reusable lemmas are L1 = 0 on the unperturbed jets and
the two L1(μ) polynomials: a stranger can run `run.sh` and
read them off the JSON.

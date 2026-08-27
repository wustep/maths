# Line QQ — T2 of the radial cubic

Status: H(7) ≥ 4 as a dent of 74 dropped. Kept: the explicit
degree-7 field, eight monomials in each component, four ovals,
Sturm vanishing of T2' only at the branch wall, and rectangle
containment. H(n) did not move.

Imagined: the T2 Chebyshev pullback of the §6 radial cubic is
an explicit degree-7 field with four hyperbolic cycles that
beats a published row (Prohens–Torregrosa H(7) ≥ 74).

It does not. Four is the sheet count. Seventy-four is the
record. The inequality 4 ≥ 74 is false, so this is not a dent
of that row.

Replay:

```bash
problems/hilbert16-limit-cycles/compute/q3/qq-t2-radial/run.sh
```

Python expands the field over Q; rustc expands it again with a
BTreeMap of monomials and a Sturm chain on T2'. The two dumps
are `diff`ed. Exit 0.

Opened this session:
[arXiv:2604.12883v1](https://arxiv.org/abs/2604.12883) and its
[HTML](https://arxiv.org/html/2604.12883v1) (Theorem 1,
Corollary 1, Lemma 3, Lemma 5, §6 cubic). The paper writes the
T3 field in §6. This line writes the T2 field the same way.

## Dropped — H(7) at least 4 as a dent of 74

The fiction needs a degree-7 field whose four hyperbolic
cycles improve the published H(7) ≥ 74 of Prohens–Torregrosa,
Nonlinearity 32 (2019), Theorem 1. The T2 pullback of a cubic
with one cycle produces exactly four cycles in degree 7. That
is the identity

$$H(2n+1)\ge 4H(n)$$

at n = 3, which is Corollary 1 of 2604.12883 and the m = 2
case of their Theorem 1. Four does not beat seventy-four.

Christopher–Lloyd, Proc. R. Soc. A 450 (1995), already have
the same four-fold H(2n+1) ≥ 4 H(n). The paper records that
this step can be read off their §3. Same four sheets at N = 7.
This line does not beat that four-fold, and that four-fold
does not beat this field. Neither is a dent of 74.

Do not cite 252, 1080, 1380, or 2012 as found here. Those
numbers are on the same arXiv, from other (n, m) lifts, and
are not this field.

## Kept — T2, two branches, four rectangles

Write T2(t) = 2t² − 1, so T2'(t) = 4t. The integer recurrence
T0 = 1, T1 = t, Tk = 2t Tk−1 − Tk−2 produces those
coefficients. The Pell identity of the paper's Lemma 3 holds
at m = 2:

$$4\,T_2(t)^2+(1-t^2)\bigl(T_2'(t)\bigr)^2=4.$$

Sturm on T2' = 4t gives one simple root in (−1, 1), namely
t = 0, and T2' is square-free. Lemma 3 of the paper takes the
walls ck = cos(kπ/m). For m = 2 those are 1, 0, −1, and the
two open branches are

$$I_1=(0,1),\qquad I_2=(-1,0).$$

T2' has no root in either open interval: the zero sits on the
common wall t = 0, not in the interior. Midpoint signs are
T2'(1/2) = 2 and T2'(−1/2) = −2. Endpoint values are
T2(1) = T2(−1) = 1 and T2(0) = −1, so each branch is a
diffeomorphism onto (−1, 1). The four open rectangles are
the products of those two intervals. On each of them
Φ(u, v) = (T2(u), T2(v)) is a product diffeomorphism and
the Jacobian T2'(u) T2'(v) = 16uv does not vanish.

## Kept — the radial cubic and the degree-7 field

The seed is the §6 cubic with ρ² = 1/4,

$$\dot x=y-x(x^2+y^2-1/4),\qquad\dot y=-x-y(x^2+y^2-1/4).$$

Polar identities, as polynomials: xP + yQ =
−(x²+y²)((x²+y²)−1/4) and xQ − yP = −(x²+y²), so
rdot = r(1/4 − r²) and θdot = −1. The circle r = 1/2 is
hyperbolic because f(r) = r(1/4 − r²) has
f'(1/2) = −1/2 ≠ 0. It sits in [−1/2, 1/2]², compactly
inside (−1, 1)².

The Chebyshev pullback is

$$\dot u=T_2'(v)\,P(T_2(u),T_2(v)),\qquad\dot v=T_2'(u)\,Q(T_2(u),T_2(v)),$$

that is (4v P(T2(u), T2(v)), 4u Q(T2(u), T2(v))). Conjugacy
DΦ · Y = λ X ∘ Φ holds with λ = T2'(u) T2'(v). Lemma 5 is
exact: deg Y = 3 · 2 + 2 − 1 = 7. Both components have total
degree 7. Expanding over Q gives eight monomials each, all
in Z[u, v]:

$$
\dot u=3v-8v^{3}-30u^{2}v+16v^{5}+32u^{2}v^{3}+48u^{4}v-32u^{2}v^{5}-32u^{6}v,
$$

$$
\dot v=11u-30uv^{2}-24u^{3}+48uv^{4}+32u^{3}v^{2}+16u^{5}-32uv^{6}-32u^{5}v^{2}.
$$

The degree-7 parts are −32 u² v (u⁴ + v⁴) and
−32 u v² (u⁴ + v⁴). The integer time-rescale 4X of the seed
(same orbits) also pulls back to degree 7. Samples of
Lemma 5 for (xⁿ, 0) and m = 2 give degrees 3, 5, 7 at
n = 1, 2, 3.

## Kept — four compact ovals

On each open I_k the values T2 ± 1/2 change sign, and
|T2| = 1 > 1/2 at the closed endpoints, so the preimage of
[−1/2, 1/2] sits strictly inside the branch. The circle
therefore lifts to one compact simple closed curve in each
of the four open rectangles, namely a component of

$$T_2(u)^2+T_2(v)^2=1/4.$$

The cleared curve 16u⁴ − 16u² + 16v⁴ − 16v² + 7 is degree 4
and does not split into four oval factors over Q. The ovals
are real components, one per rectangle. Each is hyperbolic
because the seed circle is hyperbolic and Φ is a
diffeomorphism on that rectangle (multiplier μ or μ⁻¹,
neither equal to 1).

This is H(7) ≥ 4 as a construction, matching Christopher–Lloyd
and Corollary 1 at the same N. It is not a dent of 74.

## Certificates

All checks are in `certs/` and in the dump that `run.sh`
diffs.

1. T2 = 2t² − 1, T2' = 4t, Pell at m = 2, T2' square-free.
   Sturm: one root of T2' in (−1, 1), zero roots in I1 and
   in I2.
2. Polar identities and f'(1/2) = −1/2. Conjugacy residual
   is the zero polynomial. Degrees: deg X = 3, deg Y = 7,
   both components 7. Eight monomials in Yu, eight in Yv.
3. Four rectangles (the products of I1 and I2). Endpoint
   |T2| = 1, T2 ± 1/2 sign changes, preimage of [−1/2, 1/2]
   strictly inside each branch. Level curve degree 4, not
   four Q-factors. Four ovals.
4. H(7) from this field is 4. Does not beat 74. Same four
   sheets as the Christopher–Lloyd four-fold at N = 7.
   Neither beats the other. Do not claim 252 / 1080 / 1380 /
   2012.

## What this is not

Not a dent of H(7) ≥ 74. Not a beat of Christopher–Lloyd,
and not a beat by Christopher–Lloyd of this field: both
give four sheets at degree 7. Not the T3 certificate of q1
line C (that one is degree 11 with nine ovals). Not a table
replay of 252, 1080, 1380, or 2012. The reusable lemma is
the expanded field: a stranger can run `run.sh` and read
eight plus eight monomials, degree 7, and four ovals off
the dump.

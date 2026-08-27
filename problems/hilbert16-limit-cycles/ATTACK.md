# Attack log — hilbert16-limit-cycles

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-27 — five imagined end-states

Method: write five completed solutions, then work backwards.
Each line is a concrete claim, not a mood. Drop as soon as it
contradicts the fetched record or fails a sanity check. Fork
if half-right. Do not force a fiction.

Published record used as the target (see RESEARCH.md):
H(2) ≥ 4 (Shi; Chen–Wang); H(3) ≥ 13 (Li–Liu–Yang); H(4) ≥ 28
and the Prohens–Torregrosa table; Han–Li n² log n table;
Chebyshev lift H(nm+m−1) ≥ m² H(n) (arXiv:2604.12883).
Bautin: a quadratic focus has cyclicity at most 3.

### A — quadratic with five cycles

Claim. There is an explicit quadratic field, a perturbation of
Shi

$$
\dot x=\lambda x-y-10x^2+(5+\delta)xy+y^2,
$$
$$
\dot y=x+x^2+(-25+8\varepsilon-9\delta)xy+\mu\, y^2,
$$

with five isolated periodic orbits, hence H(2) ≥ 5.

Sanity going in: four small cycles at one focus contradict
Bautin. A (3,2) or (2,2,1) configuration does not. The
published record has no accepted H(2) ≥ 5.

### B — cubic with fourteen cycles

Claim. There is an explicit cubic with 14 isolated periodic
orbits, beating Li–Liu–Yang H(3) ≥ 13. Either their
(5:1|1:5)+1 configuration plus one extra Hopf nest, or a
Giné–Gouveia–Torregrosa local 12 plus two large cycles.

Sanity going in: 2023–2026 papers we opened still cite 13 as
the global cubic record. Local M(3) ≥ 12 does not beat 13.

### C — Chebyshev replication, missed lift

Claim. Independently prove

$$
H(nm+m-1)\ge m^2 H(n),
$$

replay the 2604.12883 arithmetic on the published seeds, and
either find a factorization they missed or write an explicit
degree-11 field with nine hyperbolic cycles (their §6 cubic
seed). If a missed factorization beats Table 1, that is a
dent of those four numbers. If not, the lemma is still a
replayable identity.

### D — exact upper bound for a restricted family

Claim. A documented one-parameter family has a sharp finite
upper bound: the cubic

$$
\dot x=y-x(x^2+y^2-\rho^2),\qquad
\dot y=-x-y(x^2+y^2-\rho^2)
$$

has exactly one periodic orbit, the circle of radius ρ, for
every ρ ∈ (0,1). Optionally: quadratic Hamiltonian fields
have none; classical Lotka–Volterra quadratics have none in
the open first quadrant.

Sanity going in: uniqueness for this radial family is
elementary in polar coordinates. It is an upper bound for a
restricted family, not for H(3).

### E — Bézout ceiling, or Bautin L1–L3

Claim. Any real polynomial map Φ of degree m has at most m²
regular real preimages of a generic point, so one-step
polynomial pullback cannot beat the Chebyshev factor m²
(answering the open non-separable question in 2604.12883
Remark 4). Alternative: the first three Lyapunov quantities
of a quadratic focus are explicit polynomials and recover
Bautin's cyclicity 3 at the level of L1, L2, L3.

Sanity going in: Bézout gives ≤ m² intersections of two
degree-m curves in the plane, counting multiplicity and
points at infinity. The Lyapunov computation is classical
and long; L1 is cheap, L3 is a famous calculation.

Workers assigned one claim each, writing under
`compute/q1/{a,b,c,d,e}/`.

## 2026-08-27 — five lines return

Replay: `problems/hilbert16-limit-cycles/compute/run_all.sh`.

### A dropped, forked

H(2) ≥ 5 is dropped. Four small cycles at one focus contradict
Bautin. A cycle surrounding both foci contradicts Coppel (unique
singularity inside a quadratic cycle). The extra μ y² term kills
the order-3 jet (primitive L1 = 27μ) and moves (0,1). Forcing a
weak focus at (0,1) inside the family either centers the origin
or leaves it at order 1; Bautin budget 1+3 = 4, not 5. Circles
about (0,1) already change sign at linear order (5 ± √554).
Numerical integration would have been residue.

Fork kept: unperturbed Shi has a weak focus of order 3 at the
origin. Poincaré–Lyapunov F through degree 8 satisfies
dF/dt = V3 (x²+y²)⁴ + O(9) with V1 = V2 = 0 and V3 = 35625/8.
Li Chengzhi L1 = L2 = 0, L3 = 57000. Exactly two real finite
equilibria; (0,1) is a strong unstable focus, charpoly
t² − 5t + 24. Python rebuilds F; C differentiates the same F
over rationals. Cert: `compute/q1/a-quadratic-five/cert.json`.

### B dropped, forked

H(3) ≥ 14 is dropped. Li–Liu–Yang is paywalled, so their 13 is
not replayed and no extra nest is written. Local M(3) ≥ 12 is
not an explicit field. Harnack: a nonsingular real cubic has at
most two ovals, so 14 algebraic cycles cannot sit on one
invariant cubic.

Fork kept: classical van der Pol
ẋ = y, ẏ = −x − μ(x²−1)y, μ>0, satisfies Liénard’s hypotheses
(F(x) = μ(x³/3 − x) odd, unique positive zero √3, F < 0 on
(0,√3), F′ > 0 on [√3,∞), F → ∞, g(x) = x), hence exactly one
periodic orbit, asymptotically stable. First-order Abelian
integral on H = (x²+y²)/2 is I(h) = πμ h(2−h), one positive
simple zero at h = 2. Not a dent of H(3) ≥ 13. Cert:
`compute/q1/b-cubic-fourteen/certificate.json`.

### C kept as replay

The identity H(nm+m−1) ≥ m² H(n) replays from the separable
Chebyshev pullback in arXiv:2604.12883v1. Integer Tm, Pell
identity, Sturm of Tm′ on (−1,1), symbolic conjugacy, and the
degree formula are checked in Python and rustc.

Missed-factorization half dropped. Exhaustive one-step lifts
N+1 = m(n+1) for N ≤ 50, Appendix A seeds only, match Table 1
and Table 2 exactly. In particular

H(14) ≥ 9·28 = 252, H(29) ≥ 9·120 = 1080,
H(31) ≥ 4·345 = 1380, H(39) ≥ 4·503 = 2012

are already on that arXiv. No other factorization of those four
N, with the same seeds, beats them. Adding H(2) ≥ 4, H(3) ≥ 13,
and extra Han–Li rows still does not. Do not cite those four
numbers as found here.

§6 half kept. For ρ² = 1/4 the radial cubic has the hyperbolic
circle r = 1/2. Its T3-pullback is an explicit degree-11 field
(19+19 monomials, both languages). T3′ = 3(2t−1)(2t+1) has no
zero in the three branch intervals; Φ is a diffeomorphism on
each of the nine open rectangles; the circle sits in
[−1/2,1/2]² ⋐ (−1,1)², so one compact oval per rectangle of
T3(u)² + T3(v)² = 1/4. This is H(11) ≥ 9, which does not beat
Han–Li 153.

Table 1 omitted twelve extra N ≤ 50 one-step values from the
same seeds (9, 32–34, 37–38, 41, 44, 47–50). Those are lifts,
not independent Hilbert numbers, and not a dent of the four
printed improvements.

Certs: `compute/q1/c-chebyshev/certs/`.

### D kept

Radial cubic uniqueness: the identities
xP + yQ = (x²+y²)(ρ² − x² − y²) and xQ − yP = −(x²+y²) hold in
Z[x,y,ρ]. Polar form ṙ = r(ρ²−r²), θ̇ = −1. For every ρ > 0
the circle of radius ρ is the unique periodic orbit. Not a
bound on H(3).

Quadratic Hamiltonian fields (H of degree ≤ 3) have dH/dt ≡ 0.
Regular compact levels are continua of periodic orbits, hence
zero limit cycles.

Lotka–Volterra ẋ = x(a+bx+cy), ẏ = y(d+ex+fy) has no limit
cycle in the open first quadrant: weighted Dulac
B = x^{α−1} y^{β−1} plus the Δ = bf − ce = 0 parallel
reduction. Exact identities, not a citation.

Python and rustc dumps of the identities are diffed. Cert:
`compute/q1/d-restricted-upper/certs/identities.json`.

### E kept, full Bautin dropped

Bézout ceiling: a real polynomial map Φ = (p,q) of degree ≤ m
has at most m² regular real preimages of any point. Regular
preimages cannot lie on a common component (det DΦ = 0 there).
The Remark 4 pullback Y = adj(DΦ)(X ∘ Φ) has
deg Y ≤ nm + (m−1). Chebyshev attains m² sheets at that budget,
so the factor m² is optimal among all degree-m maps, not only
separable ones. Iterated non-separable growth is still open.

Bautin L1, derived twice (polar averaging and Poincaré V1):

L1 = (a20+a02)a11 − (b20+b02)b11 − 2 a20 b20 + 2 a02 b02.

Vanishes on Hamiltonian, y-axis reversible, holomorphic, and
unperturbed Shi; equals −2 on ẋ = −y+x², ẏ = x+x². V2 is
computed and vanishes on those families. L1 = L2 = L3 = 0 ⇒
center is dropped.

Lean 4.32.0, no mathlib: T2 recurrence, 2×2 adjugate identity,
four integer points on two quadrics (`AdjBezout.lean`).

Certs: `compute/q1/e-bezout-bautin/*.json`.

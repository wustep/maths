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

## 2026-08-27 — q2: twenty-five new imagined end-states

Same method as q1, new claims. The twenty-five one-sentence
fictions, the one-line why-it-might-work / why-it-might-die, and
the ranking live in `compute/q2/ideas.md`. They are not A–E
recycled.

Published record unchanged: H(2) ≥ 4, H(3) ≥ 13, H(4) ≥ 28,
Prohens–Torregrosa table, Han–Li, Chebyshev identity. Coppel 1966
and Llibre–Schlomiuk 2004 are now fetched (RESEARCH.md).
Li–Liu–Yang full text is still 403.

Five lines scored by (published-record delta) × (checkability
tonight) and assigned under `compute/q2/{f,i,o,p,q}/`. Discarded
on the same theorems that killed A/B, with no new bypass: Ye
class I two cycles, invariant-line two cycles, (2,2), Liénard
(3,1) two cycles, two-hemicycle H(2)≥6, Shi equator as a fifth
planar cycle, QW3 fifth cycle, figure-eight 14, Yu–Han 12+2.

Workers write the imagined certificate first, then try to verify
it. Drop as soon as a theorem or a replayed identity contradicts
the fiction. Keep a fork if it is still a finite checkable claim.

## 2026-08-27 — five q2 lines return

Replay: `problems/hilbert16-limit-cycles/compute/run_all.sh`
(q1 then q2). Exit 0.

### F dropped, forked

A homogeneous field of degree n does not have n isolated cycles.
Scaling (x,y,t) ↦ (λx, λy, λ^{1-n} t) sends any compact orbit
off the origin to a distinct orbit. Polar ṙ = r^n f(θ) does not
rescue the fiction: zeros of f are not cycles.

Fork kept: unperturbed homogeneous fields have zero isolated
periodic orbits. If xP+yQ ≡ 0 the circles about the origin are
a continuum; otherwise the zeros of xQ−yP are invariant rays.
The quasi-homogeneous center ẋ=2y, ẏ=−x³ is Hamiltonian for
H=x⁴+4y²; regular levels are a period annulus. Not a bound on
H(n). Cert: `compute/q2/f-homogeneous/certs/identities.json`.

### I dropped, forked

No Liénard field beating B(n) of arXiv:2608.17773v1 Theorem 3
was written. Full H(3,1)=1 is dropped: a quadratic term in F
kills oddness.

Fork kept: B(n) versus Han–Romanovski / Xiong–Han / Xiong
replays on n=2..40; Δ₁>0 iff n≥7, Δ₂>0 iff n≥13, as they
state. Named family ẋ=y−(αx+βx³), ẏ=−x: energy
dE/dt=−αx²−βx⁴. If α≥0, β≥0, not both zero, no cycle. If
β>0, α<0, Liénard uniqueness (exactly one). Not a bound on
H(3). Certs: `compute/q2/i-lienard/certs/`.

### O dropped, forked

k-fold complex squaring of the radial cubic does not beat
Theorem 2 of 2604.12883. Φ=(u²−v², 2uv) is z↦z²: two regular
real preimages, not four. After k steps, N=(n+1)2^k−1 and the
actual sheet count is 2^k=(N+1)/(n+1), linear in N. Bézout
still caps each degree-2 step at 4; Chebyshev of degree 2^k
attains that at the same N. Remark 4, for this map: iteration
does not escape the quadratic envelope and does not even
attain m² per step.

Certs: `compute/q2/o-iterated-squaring/certs/`.

### P dropped, forked

H(n)+Har(m) beats no published table entry for N=n+m≤50.
All 1225 pairs checked. Har(1)=0, so the recurrence is weaker
than H(n+1)≥H(n)+1. Toy: H(2)+Har(4)=8 vs H(6)≥53. The
Kolmogorov print H_K(5)≥28 is already on arXiv:2510.11705 and
uses the unreplayed H(4)≥28 seed. Do not cite it as found here.

Certs: `compute/q2/p-harnack-recurrence/certs/`.

### Q dropped, forked

H(4)≥29 is dropped. Their order-5 budget is already 28; no
term-by-term 28-cycle field is on the page.

Fork kept: the primitive Darboux field of their Proposition 6
is explicit of degree 4,

ẋ = y(x³+2x²−xy²−3x+4),
ẏ = 15x⁴−21x³+3x²y²−15x²+7xy²−11x−2y⁴+6y²,

with linear centers at (0,0) and (1,±2) and dH/dt≡0. Regular
levels are continua (zero limit cycles). Coppel contact
identities: a quadratic restricts to degree ≤2 on a line;
three collinear finite equilibria force a line of equilibria;
unperturbed Shi has exactly two real finite equilibria.
Not a bound on H(4). Cert: `compute/q2/q-pt-darboux/certs/`.

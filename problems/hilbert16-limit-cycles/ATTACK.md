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

## 2026-08-27 — q3: ten new imagined end-states

Same method. Absorb q2: the PT Darboux seed is explicit; the
quasi-homogeneous annulus ẋ=2y, ẏ=−x³ is certified; z↦z² is
2-to-1 so the next map is z↦z³; Li–Liu–Yang is still paywalled,
so a 14th cubic cycle has to be written from a Hamiltonian we
own. The ten one-sentence fictions and the ranking live in
`compute/q3/ideas.md`. They are not A–E and not the q2 five.

Official three by (published-record delta) × (checkability
tonight): FF two-well 14, GG PT L1 rank 29, HH qh M1 four zeros.
Two extras so the menu was not idle: II holomorphic cube, JJ
weak Hilbert Z(2,n). Pruned: KK constructive +1, OO five
Abelian zeros, LL cubic+line, MM Abel two zeros, NN PT algebraic
extra.

## 2026-08-27 — five q3 lines return

Replay: `problems/hilbert16-limit-cycles/compute/run_all.sh`
(q1 then q2 then q3). Exit 0.

### FF dropped, forked

Fourteen zeros of I(h), hence H(3) ≥ 14, is dropped. The first
Melnikov integral on the two-well cubic is elliptic. One exact
sample and a nonzero L1 prove I ≢ 0; they do not locate 14 roots.

Fork kept. Unperturbed ẋ=y, ẏ=x−x³. Equilibria (0,0) saddle
(det −1) and (±1,0) centers (det 2). H = y²/2 + x⁴/4 − x²/2,
so H(0,0)=0, H(±1,0)=−1/4, and dH/dt ≡ 0. Named perturbation
ẏ = x−x³+μ(1−x²)y: dH/dt = μ y²(1−x²) and
I(h) = ∮ μ(1−x²) y dx. On each figure-eight lobe, I(0)=4μ/15.
At the well bottom, I(−1/4)=0. Regular isolated zeros exhibited:
none. After the q1 focal scaling, L1 = √2 μ at both wells
(V1 = L1/8). Trace at the wells stays 0, so a Hopf birth is
not proved and two cycles are not claimed. The saddle stays a
saddle. Not a bound on H(3). Certs:
`compute/q3/ff-two-well/certs/`.

### GG dropped, forked

H(4) ≥ 29 is dropped. The unperturbed field is a Darboux center,
so every Lyapunov quantity vanishes. Prohens–Torregrosa already
stopped at 28 at order 5; their first-order count is 22, not 29.
No explicit 28-cycle perturbation is written here.

Fork kept. Linearizations replayed: (0,0) det 44; (1,±2) det 64;
all traces 0. The q1 polynomial L1_E is only the quadratic piece.
The cubic jet adds 3 a30 + a12 + b21 + 3 b03. Unperturbed L1 is
0 at all three centers (at (1,±2) the pieces ±9/2 cancel).
Location-preserving L1(μ): μ x(x−1)² y gives L1 = 0, −μ, μ;
μ x²(x−1)² gives a nonzero multiple of μ at all three. Three
Hopf cycles would be H(4) ≥ 3, not 29. Cert:
`compute/q3/gg-pt-lyapunov/certs/lyapunov.json`.

### HH dropped, forked

Fourteen zeros of I(h) on the quasi-homogeneous annulus, hence
H(3) ≥ 14, is dropped. A general cubic perturbation has
I(h) = h^{3/4}(c0 + c1 √h + c2 h), at most two positive zeros.
Gavrilov–He–Xiao arXiv:2606.22137 already treat this oval family.

Fork kept. Unperturbed ẋ=2y, ẏ=−x³, H=x⁴+4y², dH/dt ≡ 0, only
eq (0,0), linearization nilpotent. Named family P=0,
Q=μ(α−x²)y: I(h)=μ(α J0 − J2)=0 iff α = C √h, at most one
h>0. First-order cyclicity ≤ 1 for this family. The slice
Q=μ y has I(h) ∝ h^{3/4}, no positive zero. Not a bound on
H(3). Cert: `compute/q3/hh-qh-melnikov/certs/identities.json`.

### II dropped, forked

Nine regular sheets from z↦z³ is dropped. Cauchy–Riemann makes
the real map 3-to-1, not 9-to-1. Same death as O.

Fork kept. CR, Jac = 9(u²+v²)², generic fibre 3, pullback
degree N=3n+2 (n=1→5, n=2→8, n=3→11). Sheets 3=(N+1)/(n+1),
linear. T3 has the same N and attains 9. Strictly weaker.
Remark 4 is negative for this holomorphic map. Certs:
`compute/q3/ii-complex-cube/certs/`.

### JJ dropped, forked

Beating Z(2,n)=⌊(n−1)/2⌋ by one extra Abelian zero is dropped.
The formula is a theorem (M(h) is a polynomial).

Fork kept. Quadratic Hamiltonian H=(x²+y²)/2 and
Q=μ y p(x²+y²). Reduced integral Ĩ(h)=h p(2h) has the same
positive zeros as I(h). For n=3, one zero at h=1/2, matching
Z(2,3)=1. For n=5, zeros at h=1/2 and h=2, matching Z(2,5)=2.
The table n=1…10 attains the formula and does not beat it.
This is cyclicity of this period annulus, not H(2). Cert:
`compute/q3/jj-weak-hilbert/certs/family.json`.

## 2026-08-27 — q3 worker pool: leftover menu and four extras

The official three plus two extras left KK, LL, OO unexplored
and MM, NN recycled. Workers were raised: those three ran, MM
and NN were not copied, and five more live lines started
(PP, QQ, RR, SS, TT). Replay still
`problems/hilbert16-limit-cycles/compute/run_all.sh`.

### KK dropped, forked

Two hyperbolic cycles, hence a constructive +1 beating nothing
on the H(4) table, is dropped. The second orbit is a Hopf
Gasull–Santana do not write.

Fork kept. Translate the radial cubic so (2,0) is the origin.
Line L=4x−15y. Degree-4 field (L P_t, L Q_t). Distance from
(−2,0) to the line is 8/√241 > 1/2 (cleared: 15>0), so the
translated circle misses the line and remains a periodic orbit
of the product. Origin of the product is non-isolated, det=0,
trace=0. Not a bound on H(4). Cert: `compute/q3/kk-plus-one/`.

### LL dropped, forked

Three cycles on a cubic with an invariant line is dropped.

Fork kept. Named cubic ẋ=16y+16x+x³, ẏ=16xy (μ=1/16). Line
y=0 is invariant, not a line of equilibria. Dulac B=1/y gives
div(BX)=(16+3x²)/y, one-signed in each open half-plane, hence
0 isolated cycles. Ye/Cherkas uniqueness is for quadratics and
was not re-proved. Cert: `compute/q3/ll-invariant-line/`.

### OO dropped, forked

Five zeros of I(h) is dropped on both readings. Circles: Z(2,3)=1.
Cubic Hamiltonian of a quadratic field: five zeros would be
H(3)≥5, not 14. Han–Yang–Yu 2009 is Hopf cyclicity 5 at one
quadratic center (Slideblast extract), not a global 13.

Fork kept. Circles, Q=μ y(α−r²): Ĩ(h)=h(α−2h), one positive
zero. Cubic H=y²/2+x³/3−x²/2 with Q=μ y: I(h)=±μ Area, no
regular zero, cyclicity ≤1 at first order. Cert:
`compute/q3/oo-five-zeros/`.

### PP dropped, forked

H(7)≥4 as a dent of 74 is dropped.

Fork kept. Christopher–Lloyd / Gasull–Santana §4: translate the
radial circle into the first quadrant, then
u̇=v P(u²,v²), v̇=u Q(u²,v²). Degree exactly 7, 8+8 monomials,
four ovals (u²−2)²+(v²−2)²=1/4, one per open quadrant.
Attains 4 sheets at N=2n+1, better than holomorphic z↦z²
(2 sheets) and equal to T2. Explicit field. Not a dent of 74.
Cert: `compute/q3/pp-christopher-lloyd/`.

### QQ dropped, forked

T2 of the untranslated radial cubic is also degree 7 with four
ovals and does not beat 74.

Fork kept. Explicit
Yu = 3v−8v³−30u²v+16v⁵+32u²v³+48u⁴v−32u²v⁵−32u⁶v
and the matching Yv (8+8 terms). T2'=4t has no zero in the
open branches. Same 4 sheets as PP at the same N. Cert:
`compute/q3/qq-t2-radial/`.

### RR dropped, forked

Seven first-quadrant Kolmogorov cycles is dropped. H_K(5)≥28
is already on arXiv:2510.11705 and was not claimed.

Fork kept. Named family ẋ=x(1−x−y), ẏ=y(1−bx−y−c x²).
Weighted Dulac B=x^{-2} y^{-1} has div(BX)/B ≡ −1, hence
0 isolated cycles in x>0, y>0. Cert: `compute/q3/rr-kolmogorov/`.

### SS dropped, forked

L2 as a source of a 14th cubic cycle is dropped. The FF wells
are order 1.

Fork kept. L1=√2 μ replays. In the q1 Poincaré gauge,
V2=−√2 μ(23μ²+18)/96 at both wells. Not the first nonzero
quantity. Cert: `compute/q3/ss-cubic-l2/`.

### TT dropped, forked

Y=(x²+y²)X with two cycles is dropped. Unperturbed ṙ=r³(ρ²−r²)
still has exactly one positive periodic orbit.

Fork kept. Polar identities for the degree-5 product; unique
circle r=ρ. This is H(5)≥1, not a +1. Cert:
`compute/q3/tt-radial-factor/`.

MM and NN were not copied. MM is the odd-cubic Liénard of
line I. NN is the Darboux first integral of line Q.

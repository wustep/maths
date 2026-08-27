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

# Walkthrough — Hilbert 16(b), H(n)

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

- Problem: `problems/hilbert16-limit-cycles`
- Model: Grok 4.6
- Date: 2026-08-27
- Problem status: open. No published H(n) moved. The second
  campaign did not move a table entry either.

## 0. What was actually missing

A finite handle on H(n): either an explicit field that beats a
published lower bound, or an exact lemma a stranger can replay.
The asymptotic n² log n story and the Ilyashenko/Écalle finiteness
theorems do not move a table entry. The degree of freedom is a
concrete polynomial field, or a pullback identity, or a restricted
upper bound — not a new status noun.

## 1. Named false starts

Five imagined end-states were written first (ATTACK.md), then
attacked backwards.

- **Quadratic with five cycles.** The extra μ y² term that was
  supposed to create a second nest at (0,1) is the same term that
  destroys Shi’s order-3 jet (primitive L1 = 27μ) and moves the
  second equilibrium. Forcing a weak focus at (0,1) by δ = −5
  either centers the origin or leaves it at order 1. Bautin then
  budgets 1+3 = 4, which is Shi’s number, not 5. A surrounding
  fifth cycle is excluded for every quadratic by Coppel: a
  quadratic limit cycle surrounds a unique singularity.
- **Cubic with fourteen cycles.** Li–Liu–Yang is paywalled. There
  is no explicit (P,Q) on the page to which one extra nest can be
  attached. Local M(3) ≥ 12 is not a field. Harnack caps a single
  invariant cubic at two ovals.

## 2. The useful failure

The 5-cycle and 14-cycle stories failed for algebraic reasons,
not for lack of integration time. That is useful: it says where
not to spend a numeric search. The leftover exact objects are
the Shi jet (why the small cycles in (3,1) can exist at all),
van der Pol’s Liénard data (a cubic that is completely counted),
and the Chebyshev pullback (how a counted seed replicates).

## 3. The click

Two clicks, both after the fictions were dropped.

First: the 2026 Chebyshev paper’s §6 cubic is not a curiosity.
In polar coordinates it is ṙ = r(ρ²−r²), θ̇ = −1, so uniqueness
is a polynomial identity, and the T3-preimage of the circle is
nine ovals for free. That is a checkable field of degree 11 with
nine hyperbolic cycles, and it is also the uniqueness lemma of
line D.

Second: Remark 4 of that paper left non-separable maps open.
Bézout already caps regular real fibers at m², and the adjugate
pullback has the same degree budget as Chebyshev. So one-step
replication cannot beat m² by changing the map. The open
question that remains is iteration, not a single covering.

## 4. The argument

- Unperturbed Shi: build a Poincaré–Lyapunov F through degree 8
  with the even-degree gauge yⁿ = 0. Then
  dF/dt = V3 r⁸ + O(9), V1 = V2 = 0, V3 = 35625/8. Cross-check
  Li Chengzhi L3 = 57000 = (64/5) V3. Two real equilibria;
  (0,1) is a strong focus.
- van der Pol: F(x) = μ(x³/3 − x) meets Liénard’s list; the
  first-order Melnikov on the linear center is πμ h(2−h).
- Chebyshev: Φ(u,v) = (Tm(u), Tm(v)),
  Y = (Tm′(v) P∘Φ, Tm′(u) Q∘Φ), deg Y = nm+m−1, m² sheets.
  Table 1 arithmetic on the published seeds matches; no missed
  factorization beats 252/1080/1380/2012.
- Restricted upper bounds: polar identities in Z[x,y,ρ];
  Hamiltonian dH/dt = 0; Lotka–Volterra weighted Dulac.
- L1 by polar averaging and by Poincaré V1; same primitive
  polynomial. Lean checks T2, adj, and four points on two
  quadrics.

## 5. Computer search

No SAT. No ODE integrator used as a bound. The machines did
exact algebra: sympy for the jets, identities, and table;
gcc over Q for dF/dt; rustc as a second expansion of the
same polynomials; lean 4.32.0 for the tiny adj lemma.
Random degree-m maps were sampled only as a Bézout sanity
check (never above m²); that sample is not a proof.

Replay: `problems/hilbert16-limit-cycles/compute/run_all.sh`.

## 6. What is proved vs still open

Proved here, and replayable:

- Unperturbed Shi is a weak focus of order 3 at the origin,
  V3 = 35625/8, with a second real focus at (0,1).
- van der Pol (μ>0) satisfies Liénard uniqueness.
- H(nm+m−1) ≥ m² H(n) as an identity, and the 2604.12883
  Table 1 arithmetic on the cited seeds.
- The radial cubic has exactly one periodic orbit.
- Quadratic Hamiltonians have no limit cycles; Lotka–Volterra
  has none in the open first quadrant.
- One-step polynomial pullback of degree m has at most m²
  regular sheets. The first Lyapunov quantity of a quadratic
  focus is the displayed L1.

Not proved, and not claimed:

- H(2) ≥ 5, H(3) ≥ 14, or any movement of a published H(n).
- Finiteness of H(n).
- The full Bautin theorem.
- The Prohens–Torregrosa and Han–Li centers (seeds are cited,
  not reconstructed).
- That the 2026 lifts H(14) ≥ 252 etc. are independent of
  those unreplayed seeds.

## Second campaign (same day)

Twenty-five new fictions (compute/q2/ideas.md). Five scored
and attacked. All five imagined dents died; five forks lived.

### 0. What was actually missing

A handle that is not Chebyshev one-step and not Shi/van der Pol
again: either a new seed, a new lift that beats m², or a
certified upper the literature treats as open. The degree of
freedom is still an explicit field or a polynomial identity.

### 1. Named false starts

- Homogeneous n-cycles: scaling produces a continuum.
- Liénard beat of B(n): no field; full H(3,1)=1 needs oddness.
- Iterated z↦z² past the quadratic ceiling: two sheets, not four.
- Harnack recurrence: 1225 pairs, no table beat.
- PT+1: their order-5 budget is already 28.

Discarded without a worker, same deaths as A/B: Ye class I two
cycles, invariant-line two, (2,2), Liénard two, two hemicycles,
Shi equator as a planar cycle, QW3 fifth, figure-eight 14,
Yu–Han 12+2.

### 2. The useful failure

Complex squaring is the model non-separable covering, and it is
worse than Chebyshev, not better. Remark 4’s remaining half
(iteration) does not get you past m² by changing the map to
z↦z². The PT seed, once written as a primitive degree-4 field,
is a concrete Darboux center a later line can perturb.

### 3. The click

Two. First: z↦z² is 2-to-1 on the plane because Cauchy–Riemann
ties the components; Bézout’s 4 is a ceiling, not a count this
map attains. Second: −B+4xA in the PT first integral cancels
from degree 5 to degree 3, so the Darboux field is genuinely
degree 4 and has three linear centers.

### 4. The argument

- Homogeneous: P(λx,λy)=λ^n P; compact orbits scale.
- Odd-cubic Liénard: dE/dt=−αx²−βx⁴; Liénard list when α<0<β.
- Φ=(u²−v²,2uv): adj identity, deg 7 for the radial cubic,
  two regular preimages, 2^k=(N+1)/(n+1).
- Har(m) table vs the q1 seeds.
- PT primitive field; Coppel: quadratics restrict to degree ≤2
  on a line.

### 5. Computer search

No SAT. No integrator as a bound. sympy / rustc identities and
integer tables. Replay: `compute/run_all.sh` (q1 then q2).

### 6. What is proved vs still open

Proved here, extra to q1: homogeneous / unperturbed
quasi-homogeneous fields have no isolated cycles; B(n)
thresholds; the odd-cubic Liénard energy identity; iterated
squaring sheet counts; Harnack arithmetic; the explicit PT
H_{4,5} Darboux field and the quadratic contact identities.

Not proved: any movement of a published H(n). Finiteness of
H(n). The 28-cycle perturbation of that Darboux field.
Li–Liu–Yang’s 13 (still paywalled).

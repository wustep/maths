# q2 — twenty-five imagined end-states

Not A–E recycled. Each line is one concrete finite claim that would
move a published H(n) or a documented-family bound. Score later is
(published-record delta) × (checkability tonight: explicit field or
a replayable identity). Discard anything that dies on Bautin / Coppel
/ Harnack the same way A/B died, unless a new bypass is written.

Published record used as the target (RESEARCH.md, q1 unchanged):
H(2) ≥ 4 (Shi; Chen–Wang); H(3) ≥ 13 (Li–Liu–Yang); H(4) ≥ 28 and
the Prohens–Torregrosa table; Han–Li n² log n table; Chebyshev lift
H(nm+m−1) ≥ m² H(n) (arXiv:2604.12883). Do not cite 252 / 1080 /
1380 / 2012 as found here.

## The twenty-five

### F — homogeneous field with n isolated cycles

Claim. A homogeneous planar field of degree n has n isolated periodic
orbits.

Why it might work: polar form ṙ = r^n f(θ), θ̇ = r^{n-1} g(θ) is
explicit; zeros of f look like invariant rays, and a circle would
be a cycle if f vanished identically.

Why it might die: if f ≡ 0 and g never zero, every circle is periodic
(a continuum). If f has isolated zeros, those are rays, not cycles.
Either way there are no isolated periodic orbits.

### G — cubic Liénard of type (3,1) with two cycles

Claim. The Liénard field ẋ = y − (αx + βx² + γx³), ẏ = −x has two
isolated periodic orbits for some explicit (α,β,γ), beating the
conjecture H(3,1) = 1.

Why it might work: Dumortier–Panazzolo–Roussarie already killed
H(m,1) = ⌊m/2⌋ at m = 6; maybe m = 3 also fails.

Why it might die: Zhang Zhifen / Liénard uniqueness apply when
f/g is strictly monotone. The odd-cubic subfamily is classical
and has exactly one cycle when it has any. No new bypass of that
list.

### H — prove H(3,1) = 1 for every cubic-damping linear-restoring Liénard

Claim. Every field ẋ = y − F(x), ẏ = −x with deg F ≤ 3 has at most
one limit cycle.

Why it might work: the family is documented as open (Lins–Neto–Pugh
for n = 3; Scholarpedia still lists the conjecture). A certified
upper of 1 would be a family dent.

Why it might die: the full family is a famous open problem, not a
one-night identity. A named subfamily (F odd, or F = αx + βx³)
is checkable and already classical.

### I — beat Chen–Dai–Kaloshin–Li B(n) for Liénard H(2n+1, 5)

Claim. An explicit Liénard with deg f = 2n+1, deg g = 5 has more
than B(n) = 2n + ⌊n/3⌋ + ⌊(n+1)/3⌋ − 2 isolated cycles, by adding
the unused origin family they left out of Theorem 3
(arXiv:2608.17773v1).

Why it might work: they say the origin contribution was omitted
only for a compatibility reason; a small-n field might realise
all three local families at once.

Why it might die: the compatibility obstruction is the point of
their paper. Constructing the field is not a finite identity.
Replay of B(n) versus Han–Romanovski is checkable and is not a
dent of planar H(n).

### J — quasi-homogeneous weight-(1,2) center, four Melnikov zeros

Claim. A one-parameter cubic perturbation of a weight-(1,2)
quasi-homogeneous center has four isolated zeros of M₁, beating
the application bound in Gavrilov–He–Xiao (arXiv:2606.22137).

Why it might work: their general formula is in terms of a
cardinality |S| − 1; a concrete weight might have extra zeros
they did not write.

Why it might die: they claim to completely solve one named
application. The unperturbed field has a period annulus, hence
zero isolated cycles.

### K — quadratic Hamiltonian, six Abelian zeros under cubic perturbation

Claim. Some quadratic Hamiltonian H of degree 3, perturbed by
cubics, has six isolated zeros of the Abelian integral I(h),
beating the published “at most 5 from one quadratic center”
(Han–Yang–Yu, as quoted in Scholarpedia).

Why it might work: six coefficients in a cubic perturbation look
like six zeros.

Why it might die: that 5 is an upper bound, not a lower bound
we can sneak past. Weak Hilbert Z(3,2) is 2 (generic) / 3
(degenerate) for the other direction (cubic Hamiltonian, quadratic
perturbation).

### L — Ye class I with two cycles

Claim. A quadratic of Ye class I (ẏ = x) has two isolated periodic
orbits.

Why it might work: the class is large.

Why it might die: Chen–Ye uniqueness, at most one. Same shape as
A/B: a published uniqueness theorem kills the fiction immediately.

### M — quadratic with an invariant line and two cycles

Claim. A quadratic with a straight-line solution has two isolated
periodic orbits.

Why it might work: the line organises the phase portrait.

Why it might die: Cherkas / Ye, at most one. Same death as L.

### N — quadratic (2,2) configuration

Claim. There is an explicit quadratic with two nests of two cycles
each.

Why it might work: Coppel’s orientation lemmas permit two nests;
Bautin budgets 3+1 = 4.

Why it might die: Zhang (c. 2000), quoted by Llibre–Schlomiuk and
Ilyashenko–Llibre: if two foci carry cycles, one nest has at most
one. No new bypass.

### O — iterated complex-squaring beats the 2604.12883 quadratic ceiling

Claim. k-fold pullback by Φ(u,v) = (u² − v², 2uv) of the radial
cubic produces more than a quadratic number of hyperbolic cycles
in the final degree, answering Remark 4 of arXiv:2604.12883 by
beating Theorem 2.

Why it might work: Remark 4 left iterated non-separable maps
open; complex squaring is the model non-separable covering.

Why it might die: Bézout still caps each degree-2 step at 4
regular sheets. After k steps the degree is N = (n+1)2^k − 1
and the sheet count is ≤ 4^k = ((N+1)/(n+1))², still quadratic.
Chebyshev of degree 2^k matches that count in one step.

### P — Gasull–Santana Harnack recurrence produces a new H(N)

Claim. The identity H(n+m) ≥ H(n) + Har(m) of arXiv:2510.11705
Corollary 2, with Har(m) = (m−1)(m−2)/2 + [1+(−1)^m]/2, beats a
published table entry for some N = n+m ≤ 50.

Why it might work: Harnack-maximal algebraic cycles plus a
published seed look like a new lift.

Why it might die: Har(4) = 4, so H(6) ≥ H(2)+4 = 8, far below
Prohens–Torregrosa 53. The recurrence is weaker than
H(n+1) ≥ H(n)+1 when m = 1, and much weaker than the Chebyshev
factor m².

### Q — Prohens–Torregrosa H_{4,5} field plus one extra Hopf

Claim. The degree-4 Darboux field of their Proposition 6,
with first integral
H = (2x⁴ − x² + y² − 2x − 2)⁵ / (8x⁵ − 5x³ + 5xy² − 10x² − 5x − 4)⁴,
admits a degree-4 perturbation with 29 isolated periodic orbits.

Why it might work: three centers, Lyapunov order 5 already gave
⟨8,12,8⟩ = 28; one more quantity at the middle focus would be 29.

Why it might die: they used the order-5 budget and stopped at 28.
Reconstructing the unperturbed field is checkable; the 29th cycle
is not a finite identity we can write tonight.

### R — Lu’s H₁₄³ hemicycle has cyclicity ≥ 5

Claim. The labelled H₁₄³ semihyperbolic hemicycle
(arXiv:2607.13785) produces five isolated cycles, a new quadratic
configuration beyond (3,1).

Why it might work: Lu proves only an existential uniform bound,
and says it is not sharp.

Why it might die: no explicit field; Coppel still forbids a
surrounding cycle of both foci; Zhang still forbids (2,2).
Residue, not a lower bound.

### S — two hemicycles give H(2) ≥ 6

Claim. The two hemicycles of a Q₃^R quadratic
(Marín–Villadelprat, arXiv:2501.16924) each produce three cycles,
hence H(2) ≥ 6.

Why it might work: they study simultaneous cyclicity and even
an alien cycle.

Why it might die: same Coppel / Zhang wall as A and N. No bypass.

### T — Ilyashenko–Llibre (σ,κ,δ) bound is a useful finite H(2) upper

Claim. Evaluated at concrete (σ,κ,δ) for a neighbourhood of
unperturbed Shi, their restricted upper bound (arXiv:0910.3443)
is a single-digit number, hence a certified finite H(2) for that
neighbourhood that is new as an explicit constant.

Why it might work: they give a formula in (σ,κ,δ).

Why it might die: the bound is huge and excludes cycles near
equilibria and infinity — exactly where Shi’s small cycles live.
Not a bound on H(2), and not sharp enough to be a family dent
beyond Llibre–Schlomiuk’s “at most four” neighbourhood.

### U — cubic Kolmogorov with seven cycles

Claim. An explicit cubic Kolmogorov field ẋ = x p, ẏ = y q with
deg(p,q) ≤ 2 has seven isolated periodic orbits in the open first
quadrant, beating M_K(3) ≥ 6 (arXiv:2304.05111).

Why it might work: 6 is local cyclicity; a large cycle around
the two axes-and-infinity graphic would be a seventh.

Why it might die: no explicit field on the page; smooth quadratic
Kolmogorov have zero cycles (Cruz–Oliveira–Torregrosa
arXiv:2509.06198). q1 already certified zero for classical
Lotka–Volterra. Dulac may kill the extra nest.

### V — algebraic conic plus three Hopf, independently of Shi

Claim. A quadratic with an algebraic limit cycle of degree 2
(Chin Yuan-shun, cited by Coppel) plus three small Hopf cycles
is a second explicit (3,1) field.

Why it might work: algebraic cycles are checkable as factors of
an inverse integrating factor.

Why it might die: this is Chen–Wang / Shi replay, not a dent of
H(2) ≥ 4. Finding the conic is a literature reconstruction, not
a new number.

### W — Binyamini–Novikov–Yakovenko double-exp is a useful H(2) upper

Claim. Their double-exponential bound on Abelian-integral zeros
(arXiv:0808.2952), specialised at degree 2, is a finite upper
bound for H(2).

Why it might work: the paper solves the tangential Hilbert 16th.

Why it might die: that is Z(m,n), perturbations of Hamiltonians,
not H(2). The constant is not a table number.

### X — figure-eight cubic Hamiltonian with 14 Abelian zeros

Claim. An explicit cubic Hamiltonian with a figure-eight level,
perturbed by cubics, has 14 isolated zeros of I(h), hence
H(3) ≥ 14.

Why it might work: detection-function papers reached 11 then 13
this way.

Why it might die: Li–Liu–Yang is still paywalled; Picard–Fuchs
dimension and Harnack cap the oval count of one invariant cubic
at two. Same death as B unless their Hamiltonian is written
down, which it is not.

### Y — Yu–Han Z₂ cubic 12 plus two large cycles

Claim. The Z₂-equivariant cubic with 12 small cycles, plus a
stability change at infinity and one surrounding cycle, is an
explicit field with 14 cycles.

Why it might work: Li–Liu obtained 13 by exactly this extra
infinity step.

Why it might die: recycled B. No explicit (P,Q) tonight, and
Harnack still caps one invariant cubic.

### Z — Christopher–Lloyd 4-fold of van der Pol beats H(7)

Claim. The classical 4-fold composition applied to van der Pol
(exactly one cycle, degree 3) produces a degree-7 field with
more than 74 cycles.

Why it might work: 4-fold is H(2n+1) ≥ 4 H(n); iterate on a
counted seed.

Why it might die: one iteration gives H(7) ≥ 4, far below
Prohens–Torregrosa 74. The identity is already in the 1995
paper and is weaker than Chebyshev at the same degree.

### AA — piecewise quadratic with 17 cycles, folded to a polynomial

Claim. A piecewise quadratic with 17 crossing cycles (beating
H_p(2) ≥ 16) is the restriction of a single polynomial field.

Why it might work: a quadratic fold can glue two half-planes.

Why it might die: the fold is not polynomial on the whole plane,
or it raises the degree and leaves the piecewise function. User
rule: piecewise only if it maps to a polynomial field. It does
not.

### BB — Llibre–Schlomiuk 18th QW3 portrait has a fifth cycle

Claim. One of the 18 QW3 phase portraits already contains five
isolated periodic orbits.

Why it might work: 18 portraits is a large census.

Why it might die: they prove a neighbourhood of the no-cycle
no-polycycle QW3 systems has at most four cycles, and the
unperturbed order-3 weak focus has none. Same Bautin wall as A.

### CC — Shi equator is a fifth planar cycle

Claim. Poincaré compactification of unperturbed Shi has a
periodic orbit at infinity that counts as a fifth limit cycle
of the planar field.

Why it might work: infinity cyclicity is a live 2026 topic
(arXiv:2608.17773).

Why it might die: a cycle of the compactification that lives
on the equator is not a periodic orbit in R². H(n) counts
planar cycles. Coppel already forbids a planar cycle around
both foci.

### DD — Gasull–Santana +1 applied to a reconstructed PT 28-field

Claim. There is an explicit degree-5 field with 29 cycles:
take the PT degree-4 28-cycle perturbation and apply
H(n+1) ≥ H(n)+1 (arXiv:2407.13465).

Why it might work: the +1 theorem is elementary (add a simple
factor).

Why it might die: the 28-cycle field is not written
term-by-term (only a Lyapunov budget on a Darboux center).
H(5) ≥ 29 would still lose to Prohens–Torregrosa H(5) ≥ 37.
The +1 map does not beat the next published seed.

### EE — inverse integrating factor of degree 1, cubic family, exact upper 2

Claim. A documented cubic family with a linear inverse
integrating factor has at most two limit cycles, and the
literature lists that upper as open.

Why it might work: Dulac with B linear is an identity.

Why it might die: the families that have a linear inverse
integrating factor are already classified (Darboux / Lotka–
Volterra type) and q1 already counted them as zero or one.
Not an open upper.

## Ranking

Score = (published-record delta) × (checkability tonight).
Delta 3 = would move a printed H(n) or a documented open family
upper. Delta 2 = would move a secondary Hilbert number (Liénard,
Kolmogorov) or answer an open remark. Delta 1 = replay / family
lemma, no table movement. Checkability 3 = explicit field or
polynomial identity. Checkability 2 = arithmetic on a published
formula. Checkability 1 = heavy analysis, no field tonight.

| # | Claim | Δ | chk | prod | Keep / discard |
| --- | --- | --- | --- | --- | --- |
| O | iterated squaring beats ceiling | 2 | 3 | 6 | pick; likely fork to quadratic ceiling |
| I | beat Liénard B(n) | 2 | 2 | 4 | pick; fork to B(n) replay + a named uniqueness |
| P | Harnack recurrence new H(N) | 2 | 3 | 6 | pick; likely replay, no beat |
| Q | PT field, H(4)≥29 | 3 | 2 | 6 | pick; 29 dies, keep Darboux seed + Coppel |
| F | homogeneous n cycles | 2 | 3 | 6 | pick; dies, keep 0 isolated cycles |
| H | prove H(3,1)=1 | 3 | 1 | 3 | subfamily only, folded into I |
| J | qh four Melnikov zeros | 2 | 2 | 4 | folded into F |
| G | Liénard (3,1) two cycles | 3 | 1 | 3 | discard: Zhang/Liénard, no bypass |
| L | Ye class I two | 2 | 3 | 6 | discard: Chen–Ye uniqueness, same as A/B |
| M | invariant line two | 2 | 3 | 6 | discard: Cherkas/Ye, same as A/B |
| N | (2,2) | 3 | 2 | 6 | discard: Zhang, same as A |
| K | six Abelian zeros | 2 | 2 | 4 | discard: published upper 5 |
| S | two hemicycles H(2)≥6 | 3 | 1 | 3 | discard: Coppel/Zhang |
| CC | Shi equator fifth | 3 | 2 | 6 | discard: not a planar cycle; Coppel |
| BB | QW3 fifth cycle | 3 | 1 | 3 | discard: LLS ≤4, Bautin |
| X | figure-eight 14 | 3 | 1 | 3 | discard: Harnack / paywall, same as B |
| Y | Yu–Han 12+2 | 3 | 1 | 3 | discard: recycled B |
| U | Kolmogorov 7 | 2 | 1 | 2 | no explicit field |
| R | H₁₄³ cyclicity 5 | 2 | 1 | 2 | residue |
| T | Ilyashenko–Llibre digit | 2 | 1 | 2 | bound huge, excludes Shi cycles |
| W | BNY is H(2) | 2 | 1 | 2 | wrong function |
| V | algebraic conic (3,1) | 1 | 2 | 2 | Shi replay |
| Z | 4-fold van der Pol | 1 | 3 | 3 | H(7)≥4, no beat |
| AA | piecewise fold | 2 | 1 | 2 | does not map to a polynomial field |
| DD | PT+1 is H(5)≥29 | 1 | 1 | 1 | loses to H(5)≥37; no explicit 28-field |
| EE | linear Dulac cubic | 1 | 2 | 2 | already counted in q1 |

Picked five, one worker each:

1. `o-iterated-squaring/` — imagined O, fork: iterated degree-2
   pullback is still quadratic in the final degree (Remark 4).
2. `i-lienard/` — imagined I (and the checkable part of H):
   replay B(n); uniqueness for ẋ = y − (αx+βx³), ẏ = −x.
3. `p-harnack-recurrence/` — imagined P: enumerate
   H(n)+Har(m) against the published table.
4. `q-pt-darboux/` — imagined Q: reconstruct the Proposition 6
   field; Coppel Theorem 2 as a quadratic contact identity.
5. `f-homogeneous/` — imagined F (and J’s unperturbed half):
   homogeneous and quasi-homogeneous unperturbed fields have
   zero isolated periodic orbits.

L, M, N, G, S, CC, BB, X, Y are discarded on the same theorems
that killed A/B, with no new bypass.

# q3 — ten new imagined end-states

Not A–E and not the q2 five (F homogeneous n-cycles, I Liénard
B(n), O iterated squaring, P Harnack recurrence, Q PT+29).
Each line is one concrete finite claim.

What q2 left on the table: an explicit degree-4 Darboux seed
with three linear centers; a quasi-homogeneous Hamiltonian
ẋ=2y, ẏ=−x³ with a period annulus; z↦z² is 2-to-1 (so the
next non-separable test is z↦z³); Li–Liu–Yang still paywalled,
so a 14th cubic cycle has to be written from an explicit
Hamiltonian we own.

## The ten

### FF — two-well cubic Hamiltonian, 14 Abelian zeros

Claim. The cubic Hamiltonian field of H = y²/2 + (x²−1)²/4,
perturbed by an explicit cubic, has 14 isolated zeros of I(h)
across the two small wells and the large annulus, hence
H(3) ≥ 14.

Why it might work: the Hamiltonian is written down (paywall
bypass). Two wells plus a large annulus is the detection-function
geometry that produced 11 then 13 in the literature.

Why it might die: Picard–Fuchs dimension is small; typical
first-order counts are 2+2+1. Harnack still caps one invariant
cubic at two ovals. Same shape as B unless I(h) actually has
14 zeros.

### GG — L1 at the three PT centers has rank 29

Claim. A general degree-4 perturbation of the reconstructed
H_{4,5} Darboux field has first Lyapunov quantities at (0,0)
and (1, ±2) whose linear parts, together with the three traces,
give 29 independent conditions, hence H(4) ≥ 29.

Why it might work: the seed is now an explicit polynomial field.
First-order Lyapunov quantities are the same L1 as q1 line E
after translation to each focus.

Why it might die: Prohens–Torregrosa already ran this through
order 5 and stopped at 28. First-order they quote 22, not 29.

### HH — perturb ẋ=2y, ẏ=−x³, four zeros of M1

Claim. A one-parameter cubic perturbation of the
quasi-homogeneous center ẋ=2y, ẏ=−x³ has four isolated zeros
of the first Melnikov function, beating the application bound
in Gavrilov–He–Xiao (arXiv:2606.22137).

Why it might work: q2 certified the unperturbed period annulus.
M1 is an explicit Abelian integral on H=x⁴+4y².

Why it might die: they claim to completely solve one named
application. M1 may have a known small upper bound (2 or 3).

### II — complex cube attains 9 regular sheets

Claim. Φ(u,v)=(u³−3uv², 3u²v−v³) (z↦z³) pulls the radial
cubic back to a degree-11 field with nine hyperbolic cycles,
matching Chebyshev T3 without being separable.

Why it might work: degree 3, Bézout ceiling 9, same budget as T3.

Why it might die: z↦z³ is 3-to-1 on the plane, not 9-to-1
(same CR obstruction as z↦z²).

### JJ — Z(2,n) = floor((n−1)/2) as a polynomial identity

Claim. For every quadratic Hamiltonian, the Abelian integral
of a degree-n perturbation is a polynomial in the energy of
degree at most floor((n−1)/2), and that degree is attained,
so the weak Hilbert number Z(2,n) equals that count.

Why it might work: Scholarpedia states Z(2,n)=⌊(n−1)/2⌋
because M(h) is a polynomial. Checkable by expanding
∮ P dy − Q dx on H=y²/2 + x²/2 (or a quadratic H).

Why it might die: classical, not a dent of H(n). Still a
replayable weak-Hilbert identity the folder does not have.

### KK — constructive +1: degree-4 field with two hyperbolic cycles

Claim. The Gasull–Santana construction H(n+1)≥H(n)+1 applied
to the radial cubic produces an explicit degree-4 field with
two hyperbolic isolated periodic orbits.

Why it might work: their +1 is elementary (a simple factor /
a new nest at a new focus). The radial cubic is counted.

Why it might die: 2 does not beat H(4)≥28. Useful only as an
explicit +1 map.

### LL — cubic with an invariant line and three cycles

Claim. An explicit cubic with a straight-line solution has
three isolated periodic orbits.

Why it might work: Ye / Cherkas uniqueness is for quadratics.

Why it might die: a linear Dulac factor along the line may
still cap the count at 1.

### MM — Abel form of the odd-cubic Liénard has two zeros

Claim. The Cherkas / Abel transform of ẋ=y−(αx+βx³), ẏ=−x
has two positive zeros for some (α,β).

Why it might die: q2 line I already has uniqueness for that
family. Recycled.

### NN — PT inverse integrating factor gives an extra algebraic cycle

Claim. The inverse integrating factor of the H_{4,5} field
has an isolated oval that is a fifth algebraic limit cycle
after a small perturbation.

Why it might die: a first integral means continua, not isolated
algebraic cycles. Same as Q’s unperturbed half.

### OO — quadratic Hamiltonian + cubic perturbation, five simple zeros

Claim. Some explicit cubic perturbation of a quadratic
Hamiltonian has five simple zeros of I(h), attaining the
published local max (Han–Yang–Yu).

Why it might work: the upper 5 is attained in the literature;
an explicit I(h) would be a replayable seed.

Why it might die: five from one center is not H(3)≥14, and
constructing the 5-zero integral may be long.

## Ranking

| # | Claim | Δ | chk | prod | Call |
| --- | --- | --- | --- | --- | --- |
| GG | PT L1 rank 29 | 3 | 2 | 6 | pick |
| FF | two-well 14 | 3 | 2 | 6 | pick |
| HH | qh M1 four zeros | 2 | 3 | 6 | pick |
| II | z↦z³ nine sheets | 2 | 3 | 6 | extra (next map after O) |
| JJ | Z(2,n) polynomial | 1 | 3 | 3 | extra (weak Hilbert) |
| KK | constructive +1 | 1 | 3 | 3 | prune |
| OO | five Abelian zeros | 1 | 2 | 2 | prune |
| LL | cubic + line, 3 | 2 | 1 | 2 | prune |
| MM | Abel two zeros | 1 | 2 | 2 | prune: recycled I |
| NN | PT algebraic extra | 1 | 2 | 2 | prune: recycled Q |

Official three: `ff-two-well/`, `gg-pt-lyapunov/`, `hh-qh-melnikov/`.
Two more started so the menu is not left idle: `ii-complex-cube/`,
`jj-weak-hilbert/`.

All five imagined dents dropped. Forks kept; see `README.md`
and ATTACK.md. No published H(n) moved.

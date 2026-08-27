# Landau 3: Legendre's conjecture

- Slug: `landau-legendre`
- List: Landau 3 in this notebook's ordering
- Status: open; conditional exponent dent $0.2253\to0.22525$
- Area: Analytic and computational number theory
- Sources: Pintz 2009; Sorenson--Webster 2024; Chamberland--Straub 2026
- Started: 2026-08-27

## Statement

For every integer $n\geq 1$, there is a prime $p$ such that

$$
n^2<p<(n+1)^2.
$$

Equivalently,

$$
\pi((n+1)^2)-\pi(n^2)>0
$$

for every $n\geq 1$. A global bound

$$
p_{k+1}-p_k<2\sqrt{p_k}
$$

would imply Legendre's conjecture, but it is stronger and is not an equivalent
formulation.

The conjecture remains open, even assuming the Riemann hypothesis. The
unconditional Baker--Harman--Pintz exponent $0.525$ for prime gaps gives
primes between sufficiently large consecutive powers $x^\alpha$ and
$(x+1)^\alpha$ only when $\alpha>1/(1-0.525)\approx2.1053$. Ingham's
work gives a prime between sufficiently large consecutive cubes.

## Published computational record

Sorenson and Webster verified the stronger Oppermann conjecture for every
integer

$$
n\leq N=70{,}500{,}000{,}000{,}000.
$$

Thus both $(n^2,n(n+1))$ and $(n(n+1),(n+1)^2)$ contain primes throughout
that range. In particular, Legendre is checked through

$$
N^2=4{,}970{,}250{,}000{,}000{,}000{,}000{,}000{,}000{,}000.
$$

This supersedes the older shorthand that the conjecture was checked only
through $2^{64}$ by maximal-prime-gap tables. The Prime Gap List community
now reports exhaustive gap analysis through $10^{20}$, but that is still far
below the square-height reached by Sorenson and Webster.

## What would count as a new result

- A verified finite extension past $N=7.05\cdot10^{13}$, with witnesses or
  primality certificates and an independent verifier.
- A smaller explicit exponent than the published conditional threshold
  $\delta=0.2253$ in the Chamberland--Straub theorem on primes between
  $x^{2+\delta}$ and $(x+1)^{2+\delta}$ for all real $x\geq1$, still under RH.
- An independently replayed documented range, or a reproducible near-miss
  table, with its scope stated exactly.

An incomplete upstream-data reconstruction or unfinished search is not a
finite lower bound. None of these outcomes proves Legendre's conjecture.

## Result of the 2026-08-27 attack

Assume RH. For every real $x\geq1$ and every

$$
\delta\geq\frac{901}{4000}=0.22525,
$$

the interval $[x^{2+\delta},(x+1)^{2+\delta}]$ contains a prime. This improves
the $0.2253$ printed by Chamberland and Straub. The exact certificate proves
that their finite and analytic ranges overlap at this smaller rational value.
It does not remove RH and does not settle the exponent $2$ case.

The computation also independently verifies both Oppermann halves for the
100,000 integers

$$
2^{32}-100000\leq n<2^{32},
$$

ending at square-height $2^{64}$. This replay is far below the published
record and is not a record extension.

Finally, the checked-in public OLC worker logs at the pinned upstream commit
have four holes and stop at $n=31{,}894{,}400{,}000{,}352$. This is an
incomplete public-data reconstruction only. It does not revise the
peer-reviewed $N=7.05\cdot10^{13}$ result.

Replay all network-free checks with
`problems/landau-legendre/compute/q1/run_all.sh`.

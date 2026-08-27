# Walkthrough — continuity of the integrated density of states

## 0. What was actually missing

The first missing degree of freedom was the dimension. Simon's 2000
sentence makes “higher-dimensional continuum” sound like one block,
but Bourgain and Klein later settled arbitrary bounded potentials in
dimensions two and three. The live edge is dimension four.

The second missing degree of freedom was the type of theorem. Wegner
estimates already give excellent continuity for many independent
random models in all dimensions. Simon's leftover allows general
ergodic correlations, so averaging one random coupling is unavailable.

## 1. Named false starts

### Delyon–Souillard boundary counting

On a lattice, two outer layers determine a solution in the box. The
space of possible boundary values has order $L^{d-1}$, which
disappears after division by the volume. In the continuum, Cauchy
data on the boundary form an infinite-dimensional function space.
There is no direct dimension count to divide by $L^d$.

### Better Landis decay

Bourgain–Klein said exactly what improvement would unlock higher
dimensions: replace the $Q^{4/3}$ term in quantitative unique
continuation by $Q^\beta$ with a smaller power. This was a plausible
target in 2013 because their discussion noted the absence of real
counterexamples.

The target disappeared in August 2026. Frank and Ivanisvili produced
real smooth bounded potentials with nonzero solutions decaying at the
$4/3$ rate in every dimension at least three.

### Smooth by adding a direction

Adding a free coordinate does smooth the DOS. The calculation is
clean and works for an arbitrary lower-dimensional DOS measure,
including one with atoms. The idea is also an immediate instance of
the standard convolution law for separable operators. It supplies a
reusable lemma, with the published record unchanged.

## 2. The useful failure

The Landis failure identifies a precise boundary on the known proof.
It does more than say that one estimate was too weak. A uniform
smaller-power estimate of the same form would contradict an explicit
smooth real solution.

This distinction matters. The 2026 construction does not create an
ergodic family with a jump in its IDS. It says that propagation from
one distant ball, by itself, cannot provide the missing dimension-four
gain through a better power.

## 3. The click

The dimension threshold is a comparison of two exponents.
Local harmonic jets of order $N$ cost about $N^{d-1}$ conditions.
A positive density of short-interval states therefore permits

$$
N\asymp \rho^{1/(d-1)}R^{d/(d-1)}.
$$

Quantitative unique continuation asks for $N$ larger than a
constant times $R^{4/3}$. The exponents agree exactly when $d=4$.
That one equality organizes the whole record: positive room in two
and three dimensions, no room at four, and the wrong sign above four.

## 4. The argument

Start with a finite-volume spectral projection onto an interval of
width $\varepsilon$, and call its normalized rank $\rho$.
Bourgain–Klein impose vanishing jets on a grid of boxes. Harmonic
polynomials through degree $N$ have dimension of order
$N^{d-1}$, so enough projected states survive when $N$ has the
scale above.

One surviving approximate eigenfunction is small to order $N$ near
the grid points. A quantitative unique-continuation inequality
propagates mass from a unit box to one such point. Its exponential
cost contains $R^{4/3}$. Absorbing that cost into the order of
vanishing requires

$$
\frac d{d-1}>\frac43.
$$

Rearranging gives a density gain $R^{(d-4)/3}$. Optimizing $R$
against the interval width produces the modulus

$$
\rho\lesssim (\log(1/\varepsilon))^{-(4-d)/8}.
$$

The exponent tends to zero at dimension four, so this chain yields no
continuity modulus there.

For comparison, a free direction changes the mechanism completely.
Fourier momentum $p$ adds energy $|p|^2$. Averaging over $p$
replaces the base DOS measure by its convolution with the free DOS.
The cumulative function becomes a fractional integral of order
$m/2$, which is continuous for every positive number of free
directions.

## 5. Computer replay

The computer work is an exact rational-arithmetic replay. Two
implementations read the committed certificates and reproduce this
table.

| $d$ | Jet power minus UCP power | Logarithmic exponent | Outcome of this method |
| ---: | ---: | ---: | --- |
| 2 | $2/3$ | $1/4$ | positive |
| 3 | $1/6$ | $1/8$ | positive |
| 4 | $0$ | $0$ | critical |
| 5 | $-1/12$ | $-1/8$ | wrong sign |

The same replay checks that $m$ free directions give local modulus
power $\min\{1,m/2\}$: square-root for one free direction and
Lipschitz for two or more.

Run it with:

```bash
cd problems/simon-ids-continuity/compute
./run_all.sh
```

## 6. Proven versus still open

Proven here is the algebraic frontier of the published
Bourgain–Klein method, the consequence of the 2026 Landis example for
any smaller-power replacement, and the free-direction convolution
lemma.

The free-direction lemma belongs to standard separable-operator
theory and carries no new-class claim. The general bounded ergodic
continuum problem in dimensions at least four remains open. A
different mechanism must either use more than one-ball unique
continuation or exploit an ergodic feature absent from the sharp
deterministic examples.

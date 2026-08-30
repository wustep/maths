# Riemann hypothesis

- Slug: `riemann-hypothesis`
- Status: open — q1 residue; published explicit window
  $0\leq\Lambda\leq0.2$ unchanged
- Area: analytic number theory
- Classifications: Hilbert 8(a), Smale 1, Clay Millennium Prize Problem
- Started: 2026-08-30

## In general

The Riemann zeta function is initially

$$
\zeta(s)=\sum_{n\geq1}n^{-s}
$$

for $\Re s>1$ and continues meromorphically to the complex plane. Its
nontrivial zeros lie in $0<\Re s<1$. The Riemann hypothesis says that every
one of them has real part $1/2$. Clay lists the problem as open.

This folder uses the de Bruijn–Newman constant $\Lambda$ as its finite handle.
The heat-deformed Riemann $\Xi$ function has only real zeros exactly for
$t\geq\Lambda$. Riemann's hypothesis is equivalent to $\Lambda\leq0$, while
Rodgers–Tao proved $\Lambda\geq0$. Polymath 15 proved an effective upper-bound
criterion and $\Lambda\leq0.22$; Platt–Trudgian's verification of RH through
height $3{,}000{,}175{,}332{,}800$ supplies the published instantiation
$\Lambda\leq0.2$.

Landau 3 is kept separately in
[`problems/landau-legendre/`](../landau-legendre/). Its exponent $0.22525$ is
conditional on RH and does not change the Clay problem.

## Precise finite question

Polymath 15 Theorem 1.2 gives $\Lambda\leq t_0+y_0^2/2$ when three inputs are
certified: RH through $X/2$, an asymptotic zero-free region at time $t_0$, and
a zero-free barrier over $0\leq t\leq t_0$. The published explicit endpoint to
beat is therefore

$$
\Lambda\leq\frac15.
$$

The first computation asks whether a complete, independently replayable
instantiation makes the right side strictly smaller than $1/5$. It also
replays a published Lehmer-pair lower-bound calculation as a check on the
opposite finite handle.

## What would count as a new bound

A dent is a strict, checkable inequality $\Lambda<c<0.2$ whose zero-height,
finite, tail, barrier, and analytic inputs have all been independently
replayed against a published source. Arithmetic on rounded table entries is
insufficient. An off-arXiv claim remains a lead until it enters the published
record and the full certificate is independently reproduced.

Rodgers–Tao already give the exact lower endpoint $\Lambda\geq0$. A stricter
lower bound would contradict RH, so replaying an older negative Lehmer-pair
bound cannot move the present record.

## Current result

The rounded Polymath Table 1 parameters $(t_0,y_0)=(0.186,0.16733)$ satisfy

$$
t_0+\frac{y_0^2}{2}=0.19999966445,
$$

but those printed decimals do not certify the extra digits. The published
theorem remains $\Lambda\leq0.2$.

The off-arXiv $0.1787854$ candidate passed its stored assembly review here.
Fresh Arb computations reproduced its finite-error majorant, infinite tail,
and 883-prism barrier at two precisions where applicable. The stored finite
range of 3,149,013 rows was parsed, and a fresh producer run matched its first
row; the remaining rows were not regenerated. The analytic bridge was not
independently reviewed. This is residue rather than a dent. The exact small
checks and retained fresh logs are in
[`compute/q1/`](compute/q1/).

## Primary sources

- [Clay Mathematics Institute, Riemann hypothesis](https://www.claymath.org/millennium/riemann-hypothesis/)
- [Rodgers–Tao, arXiv:1801.05914](https://arxiv.org/abs/1801.05914)
- [Polymath 15, arXiv:1904.12438](https://arxiv.org/abs/1904.12438)
- [Platt–Trudgian, arXiv:2004.09765](https://arxiv.org/abs/2004.09765)

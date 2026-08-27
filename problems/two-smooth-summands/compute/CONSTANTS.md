# Constants we actually certified

Do not read this as an exponent improvement. Balog 1989 remains the
published binary record.

## Trivial covering (not a dent)

For every integer $n\ge 2$,
$$
F(n)<2\sqrt n+1,
$$
via $n=m^2+r$ or $n=(m-1)^2+(2m-1)$. Independently checked on
$[2,2\cdot 10^5]$ and on a handful of $10^{12}$–$10^{18}$
spot checks (`certs/trivial_cover.json`). Balog already calls the
$N^{1/2}$ statement almost trivial.

## Exact pointwise value

$$
F(131\,486\,759)=83.
$$
Lower bound: $131486759\equiv 7\pmod 8$ and $(-m/q)=1$ for every
odd prime $q\le 79$, so the Jacobi obstruction forbids two
79-smooth summands. Upper bound:
$649+131486110$ with $649=11\cdot 59$ and
$131486110=2\cdot 5\cdot 7^2\cdot 53\cdot 61\cdot 83$.
There is no prime strictly between 79 and 83.

## Certified $G(y)$

See `certs/g_certified.json`. Through $y=79$ this independently
reproduces OEIS A062241. In particular
$$
G(73)=G(79)=131\,486\,759,
$$
with $727473$ 73-smooth and $808372$ 79-smooth integers through
that point.

## Exact exception lists on a prefix (residue)

Integer tests, C sweep plus Python recomputation of every listed $F$:

| statement | range | exceptions | last |
| --- | --- | --- | --- |
| $F(n)\le n^{1/2}$ | $n\le 10^6$ | $3,7,23$ | 23 |
| $F(n)\le n^{2/5}$ | $n\le 10^6$ | 16 values, see `f_exceptions_exact.json` | 479 |
| $F(n)\le n^{1/3}$ | $n\le 3\cdot 10^5$ | 76 values | 18191 |

These lists are **not** a proof for all large $n$. Balog–Sárközy
already have $n^{2/5}$ for large $n$; Balog 1989 has
$n^{0.2695+\varepsilon}$. A prefix with no further exception is
search residue.

## What we did not obtain

- No explicit $\varepsilon<1/2$ with an infinite checkable covering.
- No finite residue cover that lifts.
- No exponent below $4/(9\sqrt e)$.
- No effective $N_0$ for Balog 1989.

## 2026-08-27 closed-form search (still not a dent)

See `q1/certs/`. Square / triangular / cube / power-of-two /
floor-divisor all have holes persisting through $n=20000$ at
$9/20$, $2/5$, $1/3$, and $27/100$. Floor-divisor and power-of-two
have explicit infinite failure families. Two-factor $u\le n^{1/5}$
matches the $F$ exception prefixes and does not lift.

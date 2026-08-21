# Research log — two smooth summands for every integer

## Status (accessed 2026-08-17)

- [Green, *100 Open Problems*, Problem 59](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
  (Dec 2025): still open. Record identified as Balog's
  $4/(9\sqrt e)\approx 0.2695$. Wooley obstruction via least
  quadratic non-residue for $p\equiv 3\pmod 4$. Link to
  [Erdős Problem #334](https://www.erdosproblems.com/334).
- Bloom #334 (page last edited 03 April 2026): **OPEN**, “cannot be
  resolved with a finite computation”. Zero claimed proofs. Two
  comments. Original sources [Er76e, p.272], [ErGr80, p.70],
  [Er82d, p.55]. Related OEIS A062241, A045535.
- Balog, Acta Math. Hungar. 54 (1989), 297–301, DOI
  10.1007/BF01952060. Primary scan in
  `compute/refs/balog-1989.pdf`. Uses Fouvry's Theorem C.2
  (distribution in APs to large moduli). Explicitly: the method
  cannot prove $N^\varepsilon$; $N^{1/2}$ is almost trivial.
- Hildebrand–Tenenbaum, J. Théor. Nombres Bordeaux 5 (1993),
  411–484: Balog–Sárközy 1984b give $N^{2/5}$; Balog 1989
  improves to $0.2695$; $N^\varepsilon$ unknown. Ternary:
  $\exp(c\sqrt{\log N\log\log N})$.
- Sárközy, Acta Math. Hungar. 67 (1995), 333–345: ternary
  $\exp\bigl((\sqrt{3/2}+\varepsilon)\sqrt{\log N\log\log N}\bigr)$.
  Not binary.
- Citation graph around Balog 1989 / Green #59 / Bloom #334
  (Hildebrand–Tenenbaum, Baker 2009, Győry–Hajdu–Sárközy
  arXiv:2006.15307, Blomer–Grimmelt–Li–Rydin Myerson
  arXiv:2111.01601, Dimitrov–Vigneri–Attias arXiv:1912.11546):
  no later all-integers binary exponent located. Scoped miss, not
  a proof that none exists.

Do not claim the Landau–Ramanujan density. Do not claim a table of
$G(y)$ as a bound.

## Published record

Write $P^+(1)=1$ and
$$
F(n)=\min_{1\le a<n}\max\bigl(P^+(a),P^+(n-a)\bigr),\qquad
G(y)=\min\{n\ge 2:F(n)>y\}.
$$

| quantity | published |
| --- | --- |
| explicit covering, every $n\ge 2$ | $F(n)<2\sqrt n+1$ (square-plus-remainder) |
| first nontrivial exponent, large $n$ | $F(n)\le n^{2/5}$ (Balog–Sárközy 1984b) |
| best binary exponent, large $n$ | $F(n)\ll_\varepsilon n^{4/(9\sqrt e)+\varepsilon}$ (Balog 1989) |
| Green / Erdős target | every fixed $\varepsilon>0$, unknown |
| ternary | $\exp\bigl(O(\sqrt{\log n\log\log n})\bigr)$ |
| Vinogradov wall | $n(p)\ll_\varepsilon p^{1/(4\sqrt e)+\varepsilon}\approx p^{0.1516}$ |

A uniform $F(n)\le n^{0.1}$ would imply $n(p)\le p^{0.1}$ for
large primes $p\equiv 3\pmod 4$, beating Burgess.

## What we certified

**Theorem (trivial, audited).** $F(n)<2\sqrt n+1$ for every
integer $n\ge 2$.

**Theorem (obstruction).** If $m\equiv 7\pmod 8$ and
$(-m/q)=1$ for every odd prime $q\le y$, then $m$ is not a
sum of two positive $y$-smooth integers. In particular
$G(y)\le A045535(\pi(y)-1)$, and $n(p)\le F(p)$ for primes
$p\equiv 3\pmod 4$.

**Theorem (pointwise).** $F(131486759)=83$, via the splitting
$649+131486110$ and the obstruction through prime $79$.

**Theorem (finite $G$).** The values of $G(y)$ for
$y\in\{1,2,3,5,\ldots,79\}$ in `compute/certs/g_certified.json`
are correct. In particular $G(73)=G(79)=131486759$. Independently
generated smooth counts: $727473$ of 73-smooth and $808372$ of
79-smooth integers through that point.

**Proposition (prefix, not a bound).** On the stated ranges, with
integer tests $F^q>n^p$:

- $F(n)\le n^{1/2}$ for $2\le n\le 10^6$ except $\{3,7,23\}$.
- $F(n)\le n^{2/5}$ for $2\le n\le 10^6$ except the sixteen
  integers
  $3,4,5,7,11,13,14,15,23,46,47,53,71,119,311,479$.
- $F(n)\le n^{1/3}$ for $2\le n\le 3\cdot 10^5$ except the
  seventy-six integers listed in
  `compute/certs/f_exceptions_exact.json`, last $18191$.

Each listed exception carries an explicit splitting that realises
$F$. Cubes $8,27,125$ satisfy $F(n)=n^{1/3}$ and are *not*
exceptions.

This is a computer-assisted prefix. It is **not** Balog–Sárközy
made effective, and it is **not** a new exponent. Balog 1989 is not
beaten.

## Covering search (failed, verified)

Templates tried, each with a hole list in
`compute/certs/covering_search.json` and
`covering_refined.json`:

- short intervals of length $n^\alpha$ for
  $\alpha\in\{1/2,0.45,0.4,1/3,0.3\}$;
- the true trivial window $2\sqrt n+1$ (zero holes, as it must);
- finite smooth-shift lists on residue classes modulo $8,24,120$;
- square-adjustment $n=(m-k)^2+r_k$ with $k\le 256$;
- Balog's reduction to $n^\alpha$-rough $n$, then short
  intervals;
- the even-to-odd identity.

None of these is an infinite covering at any $\varepsilon<1/2$.
The modulus-$8$ shift list at $\alpha=0.4$ fails in a single
class, which is a near-miss only on a short prefix.

## Classification (integer)

The Bambah–Chowla-style covering uses $m=\lfloor\sqrt n\rfloor$
and $r=n-m^2$. The two-point test for $F(n)\le n^{p/q}$ is
$F^q\le n^p$. Floating-point $\mathtt{pow}$ is not this test:
it misclassified $8,27,125$ as $n^{1/3}$ exceptions until the
comparison was rewritten with $128$-bit integer powers.

Balog's hard case is $p(N)>N^\alpha$. His weight is the Dirichlet
convolution $u*v*z$ supported on
$$
(N^\delta,2N^\delta]\times
(N^{1/18-\delta},2N^{1/18-\delta}]\times
\{N^{4/9-2\delta}<h\le 2N^{4/9-2\delta}:P^+(h)\le N^\alpha\}.
$$
The threshold $\alpha>4/(9\sqrt e)$ is where the $z$-sum
$1-\log((4/9)/\alpha)$ stays positive. We did not make Fouvry
effective, and we did not rerun this weight as a search: without
the distribution theorem it is another finite template.

## What would count as a dent, and why tonight is not one

A dent is an explicit $\varepsilon<1/2$ with a checkable
construction that works for all large $n$, or a certified residue
cover that implies an infinite statement, or an exponent below
$4/(9\sqrt e)$. A last exception on $[2,10^6]$ is not $N_0$.
A reproduction of A062241 is not a bound. The Vinogradov wall
blocks any claim of $\varepsilon\le 0.15$ by a cover that would
also bound $n(p)$.

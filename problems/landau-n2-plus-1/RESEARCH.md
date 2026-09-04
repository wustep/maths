# Research

## The problem

Landau, ICM Cambridge 1912, listed four prime questions he called unattackable.
The fourth: are there infinitely many primes of the form $n^2+1$? Still open
(also a special case of Hilbert 8). Unrefereed 2026 preprints claiming a proof
are not used.

## Theorems that sit next to it

- Iwaniec, *Invent. Math.* 47 (1978), 171–188. Infinitely many $n$ with
  $\Omega(n^2+1)\le 2$ (prime factors counted with multiplicity). The
  lower bound has the shape $\gg N/(\log N)^{3/2}$. This is a theorem about
  $P_2$s, not about primes.
- Friedlander–Iwaniec, *PNAS* 94 (1997). Infinitely many primes $x^2+y^4$.
  The case $y=1$ is Landau 4 and is not covered.
- Grimmelt–Merikoski, arXiv:2505.00493 (2025). The largest prime factor of
  $n^2+1$ is $\ge n^{1.312}$ infinitely often.
- Brun: $O(\sqrt{x}/\log x)$ primes $n^2+1\le x$. An upper bound of the
  same order as the conjectured main term, so it does not decide infinitude.

## Conjectural count

Hardy–Littlewood conjecture E, Shanks's constant, Bateman–Horn for
$f(n)=n^2+1$, and OEIS A199401 are the same product

$$
C_q=\prod_{p\ge 3}\Bigl(1-\frac{(-1)^{(p-1)/2}}{p-1}\Bigr)
=1.372813462818246009112192696727\ldots.
$$

Bateman–Horn gives
$\#\{n\le N:n^2+1\text{ prime}\}\sim C_q\int_2^N dt/\log(t^2+1)$.
Wolf rewrites the same thing at the prime scale $x=n^2$ as
$\pi_q(x)\sim (C_q/2)\int_2^x du/(\sqrt{u}\log u)=C_q(\mathrm{li}(\sqrt{x})-\mathrm{li}(\sqrt{2}))$.

The two numerical forms differ by $O(1)$ on our range (the integral uses
$\log(t^2+1)$ rather than $2\log t$).

## Published computational record we cite

- Wolf, arXiv:0803.1456 (2008–2010). Complete list of primes $m^2+1<10^{20}$.
  Table I is the $\pi_q(10^k)$ column we match through $k=12$.
- OEIS A083844. The same counts, extended by Gerbicz, Wolf–Gerbicz, and
  Grantham through $k=28$.
- Grantham–Graves, arXiv:2502.03513 (2025). All such primes up to
  $6.25\times 10^{28}$.
- OEIS A005574 / A002496 b-files: first 10000 values of $n$ and of $n^2+1$.
  The 10000th $n$ is 158704.
- OEIS A331942: Hardy–Littlewood prediction for those counts, rounded.
  $a(12)=53970$, against our integral $53969.85$ at $N=10^6$.

A previously unpublished prime $n^2+1$ would need $n\gtrsim 2.5\times 10^{14}$.
We did not produce one. A complete Iwaniec-$P_2$ table on a stated range is
not in those sources.

## Local arithmetic

Odd $n>1$ make $n^2+1$ even and greater than 2. Only $n=1$ and even $n$
can work. A prime divisor of $n^2+1$ is $2$ or $\equiv 1\pmod 4$.
$n^2+1=p^2$ is Pell and has no solution for $n\ge 1$, so an Iwaniec $P_2$
that is composite is a product of two (not necessarily distinct, but in fact
distinct) primes.

The first sieve on this folder counted $\omega\le 2$ and called the result
$P_2$. That is the wrong predicate: $18^2+1=325=5^2\cdot 13$ has
$\omega=2$ and $\Omega=3$.

## 2026-09-04 session log

Opened, this run:

- https://arxiv.org/abs/0803.1456 — Wolf v3 (2010). Hunt for primes $m^2+1<10^{20}$. `arxiv_fetch.py` returned HTTP 429; abs page and HTML used instead.
- https://arxiv.org/html/0803.1456v3 — Table I: $\pi_q(10^{13})=156081$, $\pi_q(10^{14})=456362$, $\pi_q(10^{15})=1339875$. $C_q=1.372813462818246\ldots$. Recast Hardy–Littlewood E as $(C_q/2)\int_2^x du/(\sqrt{u}\log u)$.
- https://arxiv.org/abs/2502.03513 — Grantham–Graves. All primes $m^2+1\le 6.25\times 10^{28}$. `arxiv_fetch.py` HTTP 429; abs page and HTML used instead.
- https://arxiv.org/html/2502.03513v1 — triple sieve; Goldbach's other other conjecture (every $a>1$ with $a^2+1$ prime is $b+c$ with both in the same set) checked to that bound. Sample code https://github.com/31and8191/Goldbach1 (not cloned).
- https://arxiv.org/abs/2505.00493 — Grimmelt–Merikoski v2. Greatest prime factor of $n^2+h$ is $\ge n^{1.312}$ infinitely often. No finite table.
- https://oeis.org/A083844 — $\pi_q(10^n)$ through $n=28$; $a(13)=156081$, $a(14)=456362$. Matches Wolf Table I on the overlapping range.
- https://oeis.org/A005574 — $n$ with $n^2+1$ prime; b-file 10000 terms, 10000th $n=158704$.
- https://oeis.org/A014233 — Miller–Rabin witness bounds. Bases $2,3,5,7,11,13$ fail at $3.474\ldots\times 10^{12}$; adding $17$ covers $3.415\ldots\times 10^{14}$; $2,3,5,7,11,13,17,19,23$ cover $3.825\ldots\times 10^{18}$.
- https://en.wikipedia.org/wiki/Miller–Rabin_primality_test — same bounds (Jaeschke / Feitsma–Galway).

Failed lookups this run:

- `python3 scripts/arxiv_fetch.py 0803.1456` and `2502.03513`: HTTP 429 from `export.arxiv.org`.
- Iwaniec, *Invent. Math.* 47 (1978) is not on arXiv; not re-fetched.

A new prime off Grantham still needs $n\gtrsim 2.5\times 10^{14}$. Not attempted. The Iwaniec $P_2$ census is not in Wolf, OEIS A083844, or Grantham–Graves.

# Attack log — Brocard–Ramanujan modular hunt

## 2026-08-16

- Environment created. Overnight quest. written: modular / covering hunt, re-run a published sieve slice,
  one Lean lemma. No attack yet. Do not claim the conjecture.

## 2026-08-16 — q1

- Lean: `FactorialMod151.lean` (p=151 interval lemma). Memory: commit 199ebaf.
- Scripts: `modular_hunt.py`, `sieve_kernel.c`, `verify_q1.py`, `plot_obstructions.py`.

## 2026-08-16 — q2

- `FactorialPrimePower.lean` builds (memory). Scripts: `unitary_factorization.py`, `verify_q2.py`.

## 2026-08-23 — q3: certificate shapes before search

The target certificate is a short list of parameterized congruence families,
not another interval scan.  Each row must contain the offset or multiplier,
the prime congruence class, the exact residue identity, and an independently
recomputed Legendre symbol.  Six shapes were considered before writing the
search.

1. **Wilson offset.**  Put $p=n+c$, with fixed $c\ge2$ and $p$ prime.
   Wilson's theorem gives
   $$
   n!\equiv\frac{(-1)^c}{(c-1)!}\pmod p.
   $$
   A row is fatal when $1+(-1)^c/(c-1)!$ is a quadratic nonresidue
   modulo every prime in a stated reduced residue class.  Dirichlet's theorem
   then makes each such prime class an infinite family of excluded indices
   $n=p-c$.  The smallest hoped-for certificate is $c=2$, where the target is
   2 and its character is controlled modulo 8.
2. **Offset-window cover.**  Generate Wilson-offset rows for several small
   values of $c$, then solve a set-cover problem on the observed indices $n$
   for which some $n+c$ is prime.  This can make a useful finite diagnostic,
   but it is not an arithmetic-progression theorem unless every claimed row
   has its own proof of infinitude.
3. **Central factorial.**  For $p=2n+1$ prime, Wilson gives
   $(n!)^2\equiv(-1)^{n+1}\pmod p$.  Substituting $n!=m^2-1$
   leaves a quartic condition on $m$.  A certificate would be a prime residue
   class on which that quartic has no root; merely observing many failures is
   not enough.
4. **Prime-square lift.**  When a Wilson-offset target is zero modulo $p$, a
   square would force divisibility modulo $p^2$.  The certificate would give
   $n!+1\not\equiv0\pmod {p^2}$ for a parameterized prime family.  This is
   stronger than a Legendre-symbol row but appears to require control of a
   Wilson quotient.
5. **Prime-power sign cover.**  Use the q2 lemma to assign each full odd
   prime-power block of $n!$ to $m-1$ or $m+1$, and seek a small CRT core for
   which every sign vector contradicts a second variable modulus.  The
   verifier would enumerate all signs and print the first surviving vector;
   q2 warns that an uncovered vector is a wall, not a lower bound.
6. **Dilated Wilson blocks.**  Try primes of the form $p=kn+r$ and partition
   $(p-1)!$ into $k$ blocks.  A certificate must reduce the block product to a
   polynomial condition on $n!$ and show it rootless in a prime congruence
   class.  Without that symbolic reduction, a numerical scan is only a lead.

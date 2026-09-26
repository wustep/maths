# q3 claim — certified $n^2+1$ census through $n=10^8$

Status: certified dent (2026-09-26). Selected leaf:
`Certified prefix n≤10^8` in `../LEAVES.md`.

Let

$$
\pi_{n^2+1}(N)=\#\{n:1\le n\le N,\ n^2+1\text{ prime}\}.
$$

Wolf, arXiv:0803.1456v3 Table I, and OEIS A083844 both record

$$
\pi_q(10^{16})=\#\{n:n^2+1<10^{16}\text{ prime}\}=3\,954\,181.
$$

$10^{16}+1$ is composite, so this is the same as $\pi_{n^2+1}(10^8)$. The
verified predicate is the conjunction of:

1. $\pi_{n^2+1}(10^8)=3\,954\,181$.
2. $\#\{n:n^2+1<10^k\text{ prime}\}$ equals Wolf Table I / A083844 $a(k)$
   for every $k=6,\ldots,16$.
3. The $\Omega=2$ list on $1\le n\le 10^8$ is complete: an independent
   C trial-bound-2003 plus Pollard scan of every even $n^2+1$ reports
   miss $=0$ and extra $=0$, and
   $\#\{n:1\le n\le 10^8,\ \Omega(n^2+1)=2\}=12\,172\,983$.
4. Both lists extend the certified $N=10^7$ prefix in `../q2/`
   (456362 primes, 1334083 $\Omega=2$ rows).

Prior notebook record: $\pi_{n^2+1}(10^7)=456362$, matching Wolf
$\pi_q(10^{14})$. Published complete prime lists: Wolf through
$m^2+1<10^{20}$, Grantham–Graves arXiv:2502.03513 through
$6.25\times 10^{28}$. This census does not produce a prime off those
lists. The new finite object is the independently certified range
$n\le 10^8$ together with the complete $\Omega=2$ table on that range.

Falsifiers: a Wolf/A083844 mismatch, a C-verifier extra or missing
prime or $P_2$, a nonzero `unsplit` leftover, or a prefix disagreement
with `../q2/`. An incomplete scan is residue, not a lower bound.

`run_all.sh` exits 0 only when the sieve, the C completeness scan, the
streaming Python multiply-back, the Wolf rows, and the $N=10^7$ prefix
all agree.

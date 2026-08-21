# Attack log — Irreducibility of random 0/1 polynomials

## 2026-08-17 — start

House: write only under `problems/zero-one-polynomials`. Target is a
certified census or an exact lemma that moves the unconditional
irreducibility problem. Isolated factor-count tables are residue unless
they beat a published bound or isolate a new obstruction.

Fetched Green 100 #93 (December 2025 / Jan 2026 PDF).

### Green 100 #93

Is a random polynomial with coefficients in {0,1} and nonzero constant
term almost surely irreducible? Precisely, writing $p_n$ for the
probability that $1+a_1x+\cdots+a_{n-1}x^{n-1}+x^n$ is irreducible,
with $a_i$ i.i.d. Bernoulli, does $p_n\to 1$?

Unconditional record in the comments: $p_n\gg 1/\log n$ (Konyagin
1999). Breuillard–Varjú: yes, assuming GRH for the Dedekind zetas of
fields $\mathbb Q(a)$ with $a$ a 0/1-polynomial root.

Bary-Soroker–Kozma: the analogous statement with coefficients uniform
in $\{1,\ldots,210\}$. Update 2023: Bary-Soroker–Koukoulopoulos–Kozma
do $\{0,1,\ldots,M\}$ for $M\ge 34$ (so $M=211$), and a positive
lower bound $\delta$ for $1\le M\le 33$. Also: Littlewood $\pm 1$
polynomials have irreducibility probability $\to 1$ along a
subsequence of degrees (Bary-Soroker–Hokken–Kozma–Poonen).

Green’s pre-2023 sentence still lists Konyagin as the best bound for
this exact ensemble. The 2023 update records BSKK’s $\delta$ for
alphabets $\{0,1,\ldots,M\}$.

### What BSKK actually prove for $\{0,1\}$

Read arXiv:2007.14567v3 / Invent. Math. 233 (2023).

- $\Upsilon_N(n)$: monic degree $n$, coefficients in a set $N$ of
  consecutive integers, constant term nonzero.
- $N=\{0,1\}$ is two consecutive integers. Conditioning on $a_0\neq 0$
  forces $a_0=1$. This *is* Green’s ensemble.
- Theorem 1(b): for $2\le N\le 34$, irreducibility probability
  $\ge\delta>0$.
- The mechanism (their §3.2, Table on p. 19): Fourier decay of uniform
  measure on $N$ consecutive integers, modulo $P=210=2\cdot 3\cdot 5\cdot 7$,
  gives $\theta=\gamma/s>0$ such that with probability $1-n^{-c}$ every
  irreducible factor has degree $\ge\theta n$. Then Lemma 3.2 (a
  count of $D\cdot I$ factorisations in $\mathbb F_p[T]$) produces
  $$
    \frac{\#\{A:\text{no divisor of degree in }[\theta n,n/2]\}}{\#\Upsilon_N(n)}
    \ge -\log(1-\theta)+O(1/n).
  $$
- Published table, $N=2$: $s=134$, $\gamma=0.50057$,
  $\theta=\gamma/s=0.003736$.
- So the published remaining factor-degree window is
  $[\theta n,n/2]$ with $\theta=0.003736$, and the published
  $\delta$ is at least $-\log(1-\theta)\approx 0.003743$ up to
  $O(n^{-c})+O(1/n)$.

Konyagin’s $1/\log n$ is superseded for this ensemble by BSKK, even
if Green’s comment sentence was not rewritten. Beating Konyagin is
not a dent. Beating $\theta=0.003736$ or isolating a new obstruction
inside $[\theta n,n/2]$ is.

### Other sources (fetched)

- Konyagin, Acta Arith. 88 (1999): $\ge c\,2^d/\log d$ irreducibles
  in $P_d$; at most $C 2^d/\sqrt{d}$ members of $P_d$ have an
  integral factor of degree $\le cd/\log d$. Method: Cohn
  ($f(2)$ prime $\Rightarrow$ irreducible) upgraded to
  $f(2)=\gamma p$ with $\gamma<1.12^{m_1}$, plus Odlyzko–Poonen
  root region $\mathrm{Re}\,z<1.14$, $|z|<2$.
- Breuillard–Varjú, Acta Math. 223 (2019), arXiv:1810.13360: GRH
  $\Rightarrow p_n\to 1$, and in fact the non-cyclotomic part is
  irreducible with probability $1-\exp(-c\sqrt{d}/\log d)$.
- Bary-Soroker–Kozma, Duke 169 (2020): alphabet $\{1,\ldots,210\}$.
- Bary-Soroker–Hokken–Kozma–Poonen, IMRN 2025: Littlewood, $n=p^r-1$
  with $2$ generating $(\mathbb Z/p^2\mathbb Z)^\times$ gives
  $P(\mathrm{irred})\ge 1-n^{-c}$. Uses $f(X+1)\equiv X^n\pmod{2}$
  plus a 2-adic Newton polygon. Does *not* transfer to 0/1: the Pascal
  matrix mod 2 is invertible, so $f(X+1)$ is just another random 0/1
  polynomial and the Newton polygon is typically flat.
- Borst–Boyd–Brekken–Solberg–Wood–Wood: exact reducibility through
  degree 20; then $10^6$ and $10^4$ Monte Carlo. Data support
  Konyagin’s conjecture that almost every reducible 0/1 polynomial is
  divisible by $x+1$.
- Filaseta–Kalogirou, arXiv:2508.12242: lacunary 0/1; Conjecture 1
  (difference-multiset map on subsets of $\{0,\ldots,n\}$ has
  $2^{n-1}+o(2^n)$ images) would imply almost every 0/1 polynomial
  has irreducible non-reciprocal part. That conjecture is implied by
  Odlyzko–Poonen and by GRH, and is open unconditionally.
- Odlyzko–Poonen, Enseign. Math. 39 (1993): zeros of 0/1 polynomials;
  the original conjecture.

### Tonight’s attacks

1. Independently recompute BSKK’s Fourier quantity $\alpha(s,\gamma;P)$
   for $N=2$, and search other 4-prime products / other $s$ for a
   larger admissible $\theta=\gamma/s$. Their table is one feasible
   pair, not claimed optimal. A larger $\theta$ shrinks the remaining
   factor-degree window and raises the explicit $\delta\ge-\log(1-\theta)$.
2. Certified exact census of $P_n$ past Borst’s degree 20, with a
   factor-degree table (to test whether anything other than $x+1$
   and cyclotomics is visible).
3. Quantitative census of Filaseta’s difference-multiset map
   (homometric 0/1 exponent sets). A proof, a disproof, or a
   sharp collision count is a lemma in the direction they isolated.

Starting with (1), because it is the published number we might beat.

## 2026-08-17 — BSKK θ is optimal for their method

Recomputed α(s,γ;P) for the uniform measure on {0,1}, |μ̂(ξ)|=|cos(πξ)|.

P=210, s=134:
- γ_max = 0.500565378865
- θ = γ_max/s = 0.003735562529
- α(s, 0.50057; 210) = 1.00002471 > 1. The published pair (s=134, γ=0.50057, θ=0.003736) is a 4·10^{-7} over-round: illegal for Theorem 7 as stated (needs α<1). The strictly feasible θ is 0.00373556.

Binding constraint is always Q=P=210, ℓ=0: S=∑_{k=0}^{209}|cos(πk/210)|^s vs √210. For large s this sum is dominated by the two ends. The first feasible integer s is 134, matching 2P/π≈133.7.

Scanned every 4-prime product of primes ≤31 with P≤15015. None beats P=210. Any larger P requires s≳2P/π and gives a smaller θ≈π/(4P).

**Residue, not a dent.** We did not beat the published remaining-degree window. We certified that the BSKK table is the optimum of their 4-prime Fourier method, up to a rounding bug.

Littlewood special-degree (BSHKP) does not transfer: f(X+1) for a 0/1 f is another random 0/1 polynomial over F_2 (Pascal matrix invertibile), so the 2-adic Newton polygon is typically flat.

## 2026-08-17 — Filaseta difference-multiset census

Implemented the map A↦A−A (as a multiset) on the 2^n subsets of {0,…,n} containing 0. Through n=26:

| n | extra_loss | extra_frac |
|---|------------|------------|
| 10 | 0 | 0 |
| 11 | 2 | 9.77e-4 |
| 13 | 20 | 2.44e-3 (peak) |
| 18 | 394 | 1.50e-3 |
| 22 | 2833 | 6.75e-4 |
| 26 | 17127 | 2.55e-4 |

extra_loss(n+1)/extra_loss(n) settles near 1.55–1.65. extra_frac is decreasing for n≥13 and is consistent with O((1.6/2)^n).

Every extra class through n=18 is a Filaseta quadruple: U·{p or p̃}·{q or q̃} with p,q non-reciprocal irreducibles and U reciprocal (often cyclotomic). First appearance n=11, matching the first n with nr_red>0 in the Z-factor census. extra_loss(n)−extra_loss(n−1) equals (1/4) of the exact-degree-n nr_red count.

This is evidence for Filaseta Conjecture 1, not a proof. The remaining obstruction inside that conjecture is 0/1 polynomials with two non-reciprocal irreducible factors.

## 2026-08-17 — exact lemma: 0/1-factor half of the obstruction is O(ρ^n)

If both non-reciprocal factors are themselves 0/1 (the “0/1 polynomials like 0/1 factors” phenomenon), the supports S,T form a direct sum: (T−T)∩(S−S)={0}. Non-reciprocal 0/1 polynomials have ≥3 terms, so S has a difference d≤deg(S)/2. The complementary factor then avoids a single difference d≤L/2 in a bit-string of length L, hence lies in a product of Fibonacci residue classes, at most 2·3^{L/2} strings.

Summing over deg S = k ∈ [3,n/2] gives at most (6+4√3)(√2·3^{1/4})^n < 13 ρ^n pairs, ρ=√2·3^{1/4}≈1.86121.

Exact enumeration of such products through n=16: 0 until n=11, then 4,12,20,32,52,96, all far below the majorant. About half of the exact nr_red count at these n is *not* a 0/1-factorization (factors have a −1). That leftover is the isolated residue for Filaseta Conjecture 1.

## 2026-08-17 — certified census of P_n

Exact Z-factorization of every element of P_n through n=20, with x+1
checked against a closed binomial formula and #irred checked against
I_2(n). Verifier green. Independent recount of n≤12 matched.

n=11 is the first degree at which a 0/1 polynomial has reducible non-reciprocal part (8 polynomials, one Filaseta quadruple-pair). Borst et al. published exact reducibility through degree 20 as a plot, no factor-type table. Our table records irred / x+1 / non-reciprocal-part status / min factor degree.

Konyagin’s conjecture (almost every reducible member of P_n is divisible
by x+1) is consistent with the table but not proved. red_not_x1 / 2^{n−1}
decreases along both parities through n=20 (even: 0.171→0.111; odd:
0.127→0.108). Not a dent of that conjecture.

n=20: 390297 irreducible out of 524288 (p_20=0.744432); 75582 divisible
by x+1; 1696 with reducible non-reciprocal part. This matches Borst’s
exact-range endpoint and adds the factor-type split they did not publish.

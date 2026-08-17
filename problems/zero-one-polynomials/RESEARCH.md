# Research log — Irreducibility of random 0/1 polynomials

## Statement (as attacked)

Green 100 #93 (December 2025 / January 2026 PDF): writing \(p_n\) for the
probability that \(1+a_1x+\cdots+a_{n-1}x^{n-1}+x^n\) is irreducible over
\(\mathbb Z\), with \(a_i\) i.i.d. Bernoulli, does \(p_n\to 1\)?

Tonight’s allowed dent: a certified finite-degree census, an explicit
remaining factor-degree regime, or a reusable exact lemma. Isolated
factor counts are residue unless they beat a published bound or isolate
a new obstruction.

## Sources fetched

- Ben Green, *100 Open Problems*, Problem 93, Jan 2026 PDF,
  https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf
- Konyagin, *On the number of irreducible polynomials with 0,1
  coefficients*, Acta Arith. 88 (1999), 333–350.
  Record before 2023: \(p_n\gg 1/\log n\).
- Breuillard–Varjú, *Irreducibility of random polynomials of large
  degree*, Acta Math. 223 (2019); arXiv:1810.13360. GRH \(\Rightarrow
  p_n\to 1\); non-cyclotomic part irreducible with probability
  \(1-\exp(-c\sqrt n/\log n)\).
- Bary-Soroker–Kozma, Duke Math. J. 169 (2020): alphabet \(\{1,\ldots,210\}\).
- Bary-Soroker–Koukoulopoulos–Kozma, Invent. Math. 233 (2023),
  arXiv:2007.14567v3. **Current unconditional record for this ensemble:**
  \(p_n\ge\delta>0\), and every irreducible factor has degree
  \(\ge\theta n\) with \(\theta=0.003736\) except for a \(n^{-c}\) set.
  Lemma 3.2 gives the explicit shape
  \(\delta\ge-\log(1-\theta)+O(n^{-c})+O(1/n)\).
- Bary-Soroker–Hokken–Kozma–Poonen, IMRN 2025: Littlewood \(\pm 1\),
  \(\limsup p_n=1\) along \(n=p^r-1\). Does not transfer to 0/1.
- Borst–Boyd–Brekken–Solberg–Wood–Wood: exact reducibility through
  degree 20 (plot, no factor-type table); Monte Carlo thereafter.
- Filaseta–Kalogirou, arXiv:2508.12242: Conjecture 1 (difference-multiset
  map has \(2^{n-1}+o(2^n)\) images) would imply that almost every 0/1
  polynomial has irreducible non-reciprocal part.
- Odlyzko–Poonen, Enseign. Math. 39 (1993): original conjecture; root
  region used by Konyagin.

Green’s pre-2023 comment still lists Konyagin as the best bound. The
2023 update records BSKK’s \(\delta\). Beating \(1/\log n\) is not a dent.

## Published theorems used

1. BSKK Theorem 7 + table p. 19, \(N=2\): \(s=134\), \(\gamma=0.50057\),
   \(\theta=\gamma/s=0.003736\), \(P=210\). We independently recomputed
   the Fourier quantity. The published \(\gamma\) is slightly illegal
   (\(\alpha=1.000025>1\)); the largest strictly feasible \(\theta\) is
   \(0.003735562529\) at the same \((P,s)\). No other 4-prime \(P\)
   improves it. Certificate: `compute/verify_fourier.py`.
2. BSKK Lemma 3.2: among polynomials with no factor of degree
   \(<\theta n\), a proportion \(-\log(1-\theta)+O(1/n)\) have no factor
   in \([\theta n,n/2]\). Combined with (1) this is the published
   \(\delta\).
3. Filaseta–Kalogirou Lemma 2: a 0/1 polynomial with two non-reciprocal
   irreducible factors (not necessarily distinct) is homometric to a
   different 0/1 polynomial of the same degree and same number of terms.
4. Kronecker: a monic integer polynomial with all roots on the unit
   circle is cyclotomic. Hence every non-reciprocal irreducible has a
   root off the circle, and every degree-1 or degree-2 monic factor of a
   0/1 polynomial is reciprocal (\(x+1\), \(x^2\pm x+1\), \(x^2+1\)).

## What this folder proves

### Theorem 1 (0/1-factor Filaseta obstruction is exponentially rare)

Let \(P_n\) be the set of monic 0/1-polynomials of degree \(n\) with
constant term 1, so \(\#P_n=2^{n-1}\). Let \(R_n^{01}\) be the number of
\(f\in P_n\) that factor in \(\mathbb Z[x]\) as \(f=AB\) with \(A,B\)
both monic 0/1 having at least three terms each. (Every non-reciprocal
0/1 polynomial has at least three terms, since \(1+x^d\) is reciprocal,
so this majorizes the both-non-reciprocal 0/1-factor count; palindromic
trinomials such as \(1+x+x^2\) are included and only help the upper
bound.) Then for every integer \(n\ge 2\),

\[
R_n^{01}
\le (6+4\sqrt{3})\,\rho^n
< 13\,\rho^n,
\qquad
\rho=\sqrt{2}\cdot 3^{1/4}\approx 1.8612097182.
\]

In particular \(R_n^{01}/\#P_n = O\bigl((0.9306)^n\bigr)\to 0\).

**Proof.** Write \(\deg A=k\in[3,n/2]\). Because \(A\) has at least
three terms, its difference set contains a positive \(d\le k/2\). The
complementary 0/1 polynomial \(B\) of degree \(n-k\) then has no two
coefficients \(1\) at distance \(d\): otherwise the convolution \(A*B\)
would have a coefficient \(\ge 2\). (There are at most \(2^{k-1}\)
monic 0/1 polynomials of degree \(k\), a convenient majorant for the
three-term subclass.)

A bit-string of length \(L=n-k+1\) with no two \(1\)s at distance \(d\),
where \(2\le d\le L/2\) (this last because \(d\le k/2\le n/4\) and
\(L-1=n-k\ge n/2\)), splits into \(d\) residue classes, each a binary
string with no consecutive \(1\)s. A class of length \(\ell\) has
\(F_{\ell+2}\) possibilities. Under \(\sum\ell_i=L\) and each
\(\ell_i\ge 2\), the product \(\prod F_{\ell_i+2}\) is maximised when
every class has length 2, giving \(3^{L/2}\). For general \(L\) one has
the uniform majorant \(2\cdot 3^{L/2}\).

There are \(2^{k-1}\) choices of \(A\). Hence the number of pairs is at
most
\[
\sum_{k=3}^{\lfloor n/2\rfloor} 2^{k-1}\cdot 2\cdot 3^{(n-k+1)/2}
= 3^{(n+1)/2}\sum_{k=3}^{\lfloor n/2\rfloor} r^k,
\quad r=2/\sqrt{3}.
\]
The inner sum is at most \(r^{n/2+1}/(r-1)\). Simplifying gives the
constant \(6+4\sqrt{3}\) in front of \(\rho^n\). Distinct \(f\) are no
more numerous than pairs. \(\square\)

Exact counts of these products (`compute/count_01_factors.py`) through
\(n=16\): \(0\) for \(n\le 10\), then \(4,12,20,32,52,96\). All lie
under the majorant (already at \(n=16\) the majorant is \(82944\)).

### Theorem 2 (certified census of \(P_n\), factor types)

For \(1\le n\le 20\), every element of \(P_n\) was factored over
\(\mathbb Z\). The counts satisfy:

- \(\#\{f\in P_n:(x+1)\mid f\}\) equals the closed binomial formula in
  `compute/closed_forms.py` (even \(n\): \(\sum_k\binom{n/2-1}{k}\binom{n/2}{k+2}\);
  odd \(n\): \(\sum_k\binom{(n-1)/2}{k}^2\)).
- \(\#\{f\in P_n:f\text{ irreducible over }\mathbb Z\}\ge I_2(n)\) for
  \(n\ge 2\), where \(I_2(n)=\frac1n\sum_{d\mid n}\mu(d)2^{n/d}\) (every
  \(\mathbb F_2\)-irreducible is \(\mathbb Z\)-irreducible).
- The number \(R_n\) of \(f\in P_n\) whose non-reciprocal part is
  reducible is \(0\) for \(n\le 10\), and is a multiple of 4 for every
  \(n\) (Filaseta quadruples). \(R_n\) equals four times the number of
  new extra homometric classes at exact degree \(n\).

| n | \(\#P_n\) | irred | \(p_n\) | \(x+1\) | red, not \(x+1\) | \(R_n\) (nr-part reducible) |
|---|----------:|------:|--------:|--------:|-----------------:|----------------------------:|
| 2 | 2 | 2 | 1.000000 | 0 | 0 | 0 |
| 3 | 4 | 2 | 0.500000 | 2 | 0 | 0 |
| 4 | 8 | 6 | 0.750000 | 1 | 1 | 0 |
| 5 | 16 | 8 | 0.500000 | 6 | 2 | 0 |
| 6 | 32 | 21 | 0.656250 | 5 | 6 | 0 |
| 7 | 64 | 34 | 0.531250 | 20 | 10 | 0 |
| 8 | 128 | 84 | 0.656250 | 21 | 23 | 0 |
| 9 | 256 | 150 | 0.585938 | 70 | 36 | 0 |
| 10 | 512 | 331 | 0.646484 | 84 | 97 | 0 |
| 11 | 1024 | 614 | 0.599609 | 252 | 158 | 8 |
| 12 | 2048 | 1417 | 0.691895 | 330 | 301 | 24 |
| 13 | 4096 | 2638 | 0.644043 | 924 | 534 | 48 |
| 14 | 8192 | 5508 | 0.672363 | 1287 | 1397 | 64 |
| 15 | 16384 | 10874 | 0.663696 | 3432 | 2078 | 148 |
| 16 | 32768 | 23437 | 0.715240 | 5005 | 4326 | 220 |
| 17 | 65536 | 44862 | 0.684540 | 12870 | 7804 | 424 |
| 18 | 131072 | 95887 | 0.731560 | 19448 | 15737 | 640 |
| 19 | 262144 | 185238 | 0.706627 | 48620 | 28286 | 1152 |
| 20 | 524288 | 390297 | 0.744432 | 75582 | 58409 | 1696 |

Verifier: `compute/verify_census.py`. SHA-256 of the reducible bitmasks
is stored per \(n\) in `census.json` for an independent replay.

### Theorem 3 (homometric census, Filaseta Conjecture 1 through \(n=26\))

Let \(\varphi\) send a subset \(A\subseteq\{0,\ldots,n\}\) containing \(0\)
to the difference multiset \(A-A\). Write \(E_n\) for the number of
missing images relative to “every fibre is exactly \(\{A,A'\}\)”. Then
\(E_n=0\) for \(n\le 10\), \(E_{11}=2\), \(E_{26}=17127\), and
\(E_n/2^n\) is decreasing for \(13\le n\le 26\), with
\(E_{26}/2^{26}\approx 2.55\cdot 10^{-4}\). Every extra class through
\(n=18\) is a Filaseta quadruple. Certificate: `compute/homometric.c`
and `compute/homometric.json`.

This is a finite verification of Filaseta Conjecture 1, not a proof for
all \(n\). Combined with Theorem 1, the only remaining source of extra
classes that is not known to be \(O(\rho^n)\) is 0/1 polynomials whose
two non-reciprocal irreducible factors are *not* themselves 0/1.

## What this folder does not prove

- \(p_n\to 1\). Still Green #93.
- Any improvement of BSKK’s \(\theta=0.003736\) or of the shape
  \(\delta\ge-\log(1-\theta)\). The 4-prime Fourier method is saturated
  at \(P=210\), \(s=134\).
- Filaseta Conjecture 1 for all \(n\). The non-0/1-factor half of
  \(R_n\) is not bounded here.
- Konyagin’s conjecture that almost every reducible \(f\in P_n\) is
  divisible by \(x+1\). The complementary proportion decreases along
  both the even and the odd subsequences through \(n=20\) (even:
  \(0.171,0.132,0.120,0.111\); odd: \(0.127,0.119,0.108\)) but is not
  proved to tend to \(0\).
- A special-degree \(\limsup p_n=1\) for the 0/1 ensemble. The
  Littlewood Newton-polygon argument is unavailable.

## Computational records we did not beat

- Borst et al. exact reducibility *probability* through degree 20: we
  match that range exactly, and add factor-type columns they did not
  publish. We did not push the exact \(n\) past 20.
- BSKK \(\theta=0.003736\): not beaten.
- Any GRH-conditional rate.

## How to replay

```
cd compute
python3 verify_fourier.py
python3 verify_census.py
python3 count_01_factors.py
# optional longer:
# python3 fourier_theta.py
# gcc -O3 -o homometric homometric.c && ./homometric 1 22
# python3 census_irred.py 1 18
```

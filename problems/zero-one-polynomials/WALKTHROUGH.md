# Walkthrough — A small $\theta$, a quadruple, a Fibonacci bound

- Problem: `problems/zero-one-polynomials` (P17 / Green 100 #93)
- Date: 2026-08-17
- Argument status: exact lemma on the 0/1-factor Filaseta obstruction,
  plus a certified census. No improvement of $p_n\to 1$.
- Problem status: open. Unconditional $p_n\to 1$ is still Green #93.

## 0. What was actually missing

The missing degree of freedom is not “count more factors”. Konyagin
already gives $p_n\gg 1/\log n$, and Bary-Soroker–Koukoulopoulos–Kozma
already give $p_n\ge\delta>0$ for this exact ensemble, by proving that
all factors have degree $\ge\theta n$ except for an $n^{-c}$ set and
then counting $D\cdot I$ factorisations over $\mathbb F_p$. Their
published $\theta$ for alphabet $\{0,1\}$ is $0.003736$.

What was on the table, and not done, was: (i) whether that $\theta$ is
the best their Fourier method can do; (ii) Filaseta–Kalogirou’s
difference-multiset conjecture, which would cut the remaining
obstruction down to reciprocal factors; (iii) an exact bound on any
named piece of that obstruction.

The 0/1-factor piece — two 0/1 non-reciprocal factors whose convolution
has no carry — is named, classical, and finite. That is the handle.

## 1. Named false starts

- **Beat Konyagin’s $1/\log n$.** Green’s pre-2023 sentence still
  lists it. BSKK Theorem 1(b) already gives a positive $\delta$ for
  $\Upsilon_{\{0,1\}}(n)$, which *is* $P_n$. Beating Konyagin is
  not a dent.

- **Special degrees, Littlewood-style.** Bary-Soroker–Hokken–Kozma–Poonen
  get $\limsup p_n=1$ for $\pm 1$ coefficients along $n=p^r-1$,
  because $f(X+1)\equiv X^n\pmod 2$ and a 2-adic Newton polygon
  supplies a factor of degree $>n-\theta n$. For 0/1 coefficients the
  Pascal matrix is invertible over $\mathbb F_2$, so $f(X+1)$ is
  just another random 0/1 polynomial. The Newton polygon is typically
  flat. Dead.

- **Improve BSKK’s $\theta$ by trying other 4-prime moduli.** The
  binding constraint at $P=210$ is the full modulus, $\sum_k|\cos(\pi
  k/210)|^s < \sqrt{210}$. The first legal $s$ is 134, matching
  $2P/\pi\approx 133.7$. Any larger 4-prime product needs a larger
  $s$ and gives a *smaller* $\theta$. We scanned 177 products. None
  won. Residue.

- **Hensel-lift a full irreducibility census past Borst’s degree 20 as
  the dent.** House rule: a factor-count table is not a dent unless it
  beats a published bound or isolates an obstruction. A longer table of
  $p_n$ alone would have been residue.

- **Prove Filaseta Conjecture 1 in full.** That is “almost every 0/1
  polynomial has irreducible non-reciprocal part”. It reduces to
  bounding the polynomials with *two* non-reciprocal irreducible
  factors. Half of those, at small $n$, have a factor with a $-1$
  coefficient. We did not bound that half.

## 2. The useful failure

The Fourier search was the useful failure. It showed that BSKK’s
$N=2$ row is not a casual Mathematica output. It is the unique
optimum of their method: smallest 4-prime modulus, first feasible
moment $s$, $\gamma$ sitting $5\cdot 10^{-4}$ above $1/2$.
Their printed $\gamma=0.50057$ even overshoots — $\alpha=1.000025$
— so the strictly legal $\theta$ is $0.00373556$, not $0.003736$.
A four-digit rounding is not a dent. What it taught is that the
remaining factor-degree window $[\theta n,n/2]$ will not move
without a new equidistribution theorem.

Once $\theta$ is frozen, the only finite obstruction that is *not*
already swallowed by BSKK for practical $n$ (namely $n<3/\theta
\approx 800$) is non-reciprocal factors of degree $\ge 3$. Degree 1
and 2 are always reciprocal. That is exactly Filaseta’s setting.

## 3. The click

Filaseta–Kalogirou Lemma 2 says: if a 0/1 polynomial has two
non-reciprocal irreducible factors, it shares its autocorrelation with
a different 0/1 polynomial of the same degree and the same number of
terms. Conversely, an irreducible 0/1 polynomial is uniquely determined
by its autocorrelation up to reciprocity (unique factorisation in
$\mathbb Z[x]$).

So extra homometric classes *are* the polynomials with reducible
non-reciprocal part. A bitmask census of difference multisets through
$n=26$ sees the first extras at $n=11$, all of them quadruples
$U\cdot\{p,p̃\}\cdot\{q,q̃\}$, and an extra-fraction that falls from
$2.4\cdot 10^{-3}$ at $n=13$ to $2.6\cdot 10^{-4}$ at $n=26$.

Among those quadruples, some are carry-free products of two 0/1
polynomials. For those, the supports $S,T$ satisfy
$(T-T)\cap(S-S)=\{0\}$. A non-reciprocal 0/1 polynomial has at least
three terms, so $S$ has a difference $d\le\deg S/2$. The
complementary bit-string avoids a single distance $d\le L/2$, hence
splits into residue classes each with no consecutive $1$s —
Fibonacci, at most $3^{L/2}$ when every class has length 2.

The sum over $\deg S\le n/2$ is a geometric series with ratio
$2/\sqrt{3}$, and closes at
$(6+4\sqrt{3})(\sqrt{2}\cdot 3^{1/4})^n$. The base is $1.861\ldots<2$.

That is the click: one forbidden difference, residue-class Fibonacci,
geometric sum, exponential decay against $2^{n-1}$.

## 4. The argument, in the order it was found

1. Fetch Green #93. Read Konyagin, Breuillard–Varjú, BSKK, BSHKP,
   Filaseta–Kalogirou, Borst et al.
2. Notice BSKK Theorem 1(b) already applies to $\{0,1\}$. The
   published $\delta$ is $-\log(1-\theta)$ with $\theta=0.003736$.
3. Recompute $\alpha(s,\gamma;210)$. Recover $\gamma_{\max}=0.500565$,
   $\theta=0.00373556$. Published $0.50057$ is illegal by
   $2.5\cdot 10^{-5}$ in $\alpha$. Scan 177 other 4-prime products.
   Lose.
4. Run the difference-multiset map on all $2^n$ subsets containing
   $0$, $n\le 26$. Extras start at $n=11$. Factor the members
   with sympy: every extra class is a Filaseta quadruple. The first
   class is
   $(x^2+1)(x^4+x+1)(x^5-x^3+1)$ and its three siblings.
5. Exact-factor every element of $P_n$ through $n=20$. The count
   $R_n$ of reducible non-reciprocal parts is $0$ until $n=11$,
   then $8,24,48,64,148,220,424,640,1152,1696$, always a multiple of
   4, and equal to four times the number of new extra homometric
   classes at that exact degree. The $x+1$ column matches a closed
   binomial formula. Irreducibles dominate $I_2(n)$.
6. Split $R_n$ into 0/1-factorisations versus the rest. The 0/1
   factorisations through $n=16$ are $0,0,\ldots,4,12,20,32,52,96$.
   Prove they are $O(\rho^n)$ by the Fibonacci argument above.
   The complementary half — factors with a $-1$ — is the residue
   inside Filaseta Conjecture 1.

## 5. Computer residue

- `compute/fourier_theta.json` — 4-prime search. Winner $P=210$,
  $s=134$. Verifier `verify_fourier.py`.
- `compute/homometric.json` — extra_loss through $n=26$. Source
  `homometric.c` (128-bit fingerprints of the difference histogram).
- `compute/homometric_pairs.json` — explicit quadruples through
  $n=18$, with sympy factorisations.
- `compute/census.json` — exact $P_n$ through $n=20$, SHA-256 of
  reducible bitmasks, min-factor-degree histogram, non-reciprocal-part
  status. Verifier `verify_census.py` against `closed_forms.py`.
  Independent recount of $n\le 12$ matched.
- `compute/count_01_factors.json` — exact 0/1-factor counts through
  $n=16$, all under the $\rho^n$ majorant.

The matrix that matters for the lemma is the $d\times d$ residue
splitting of a length-$L$ string with one forbidden distance: each
block is a path of no-consecutive-$1$s, and the worst product of
Fibonacci numbers at $d=L/2$ is $3^{L/2}$.

## 6. What is proved vs still open

**Proved.** $R_n^{01}<13\rho^n$ with
$\rho=\sqrt{2}\cdot 3^{1/4}$. The 0/1-factor half of Filaseta’s
obstruction is exponentially smaller than $P_n$. The BSKK
$N=2$ Fourier row is optimal for 4-prime moduli and slightly
over-rounded. Exact factor-type census of $P_n$ through degree 20,
internally consistent with closed forms. Homometric extra-fraction
computed through $n=26$ and identified with $R_n$.

**Still open.** $p_n\to 1$. Any $\theta>0.003736$. Filaseta
Conjecture 1 in full (the half of $R_n$ whose factors have a
negative coefficient). Konyagin’s “almost every reducible is
divisible by $x+1$”. A special-degree $\limsup p_n=1$ for 0/1
coefficients.

The remaining named obstruction, after tonight, is: 0/1 polynomials
that factor as $w_1 w_2$ with both $w_i$ non-reciprocal,
non-0/1, and of degree at least 3. The first examples are already in
the $n=11$ quadruple: $x^5-x^3+1$ is not 0/1.

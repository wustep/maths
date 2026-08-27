# Attack log — two smooth summands for every integer

## 2026-08-17 — literature (fetched before any search)

Fetched, in order:

- Green, *100 Open Problems* (Dec 2025 update), Problem 59, p.29 of
  `compute/refs/green-100-open-problems.pdf`:
  “Is every $n\le N$ the sum of two integers, all of whose prime
  factors are at most $N^\varepsilon$?” Comments: asked by Erdős
  (1981 collection [110]): if $f(n)$ is the least integer not of
  the form $a+b$ with $P^+(ab)\le n$, then for every $k$ and
  $n>n_0(k)$ one should have $f(n)>n^k$. “This conjecture does
  not look hard but I could not get anywhere with it.” Record still
  Balog’s exponent $4/(9\sqrt{e})\approx 0.2695$ from 30 years ago
  [16]. Wooley: if a prime $p\equiv 3\pmod 4$ is a sum of two
  $p^\varepsilon$-smooth numbers then there is a quadratic
  non-residue $\le p^\varepsilon$. Solving the problem for every
  $\varepsilon>0$ is therefore at least as hard as Vinogradov’s
  least quadratic non-residue on that prime class. Best
  unconditional exponent there is $1/(4\sqrt{e})\approx 0.1516$.
  Known under GRH.
- [Erdős Problem #334](https://www.erdosproblems.com/334) (accessed
  2026-08-17; last edited 03 April 2026). Status: **OPEN**, “cannot
  be resolved with a finite computation”. Zero claimed proofs. Two
  comments (my99n, 03 Mar 2026; Woett, 19 Nov 2025). Cites
  [Er76e, p.272], [ErGr80, p.70], [Er82d, p.55]. Related OEIS
  [A062241](https://oeis.org/A062241), [A045535](https://oeis.org/A045535).
- Balog, *On additive representation of integers*, Acta Math. Hungar.
  54 (1989), 297–301, DOI 10.1007/BF01952060. Primary scan saved as
  `compute/refs/balog-1989.pdf`. Theorem: every $N>N_0(\varepsilon)$
  is $a+b$ with $P^+(ab)\le N^{4/(9\sqrt{e})+\varepsilon}$.
  Opening paragraph: Erdős called $N^{1/3}$ “the first non-trivial
  question because the statement with $N^{1/2}$ in place of
  $N^{1/3}$ is almost trivially true.” The method “cannot be enough
  to prove even $N^\varepsilon$” and is not self-contained: it
  invokes Fouvry’s large-modulus distribution theorem. A weaker
  exponent is available from the large sieve alone.
- Hildebrand–Tenenbaum, *Integers without large prime factors*,
  J. Théor. Nombres Bordeaux 5 (1993), 411–484. Additive paragraph
  (p.469 of the scan): Balog–Sárközy 1984b give $P^+(n_i)\le N^{2/5}$;
  Balog 1989 improves to $0.2695\ldots$; it is not known whether
  $P^+(n_i)\le N^\varepsilon$ holds for any fixed $\varepsilon>0$.
  Ternary: Balog–Sárközy 1984a give
  $P^+(n_1n_2n_3)\le\exp(c\sqrt{\log N\log\log N})$.
- Sárközy, *On sums with small prime factors*, Acta Math. Hungar. 67
  (1995), 333–345 (DOI 10.1007/BF01874496): ternary bound
  $\exp\bigl((\sqrt{3/2}+\varepsilon)\sqrt{\log N\log\log N}\bigr)$.
  Not a binary improvement.
- Balog–Sárközy, *On sums of sequences of integers, I*, Acta Arith.
  44 (1984), 73–86 (`compute/refs/balog-sarkozy-1984-acta-arith.pdf`):
  this is the dense-sumset cousin (a sum $a+b$ from two dense
  sequences is smooth), not the two-smooth-summands theorem.
- OEIS A062241 (Schroeppel / Wilson / Johnson): smallest $n\ge 2$
  that is not a sum of two $\mathrm{prime}(k)$-smooth positive
  integers. Terms through $a(29)=2570169839$, with $a(30)$
  uncomputed as of Donovan Johnson, Aug 2010.
- OEIS A045535: least negative pseudosquare modulo the first $n$
  odd primes (Lehmer–Lehmer–Shanks; b-file through $n=50$ by
  Dobbelaere, Feb 2021). A062241($k$) tracks A045535($k-1$) on
  the computed range; Touch Sungkawichai (Mar 2026) states
  $a(n)\le A045535(n-1)$.
- Dimitrov–Vigneri–Attias, arXiv:1912.11546: cryptographic
  “anti-Goldbach” conjecture $F(n)=O((\log n)^{2+\varepsilon})$.
  Heuristic / algorithmic; no theorem.
- Citation graph check (Balog 1989 DOI, Green #59, Bloom #334,
  Hildebrand–Tenenbaum, Baker 2009 survey, Győry–Hajdu–Sárközy
  arXiv:2006.15307, Blomer–Grimmelt–Li–Rydin Myerson arXiv:2111.01601):
  no later all-integers binary exponent. Scoped miss, not a proof
  that none exists.

Published record I must beat, after the fetch:

| quantity | published |
| --- | --- |
| trivial explicit covering | $F(n)<2\sqrt{n}+1$ for every $n\ge 2$ (square-plus-remainder; Balog: “almost trivially true”) |
| first nontrivial exponent, large $n$ | $F(n)\le n^{2/5}$ (Balog–Sárközy 1984b) |
| best binary exponent, large $n$ | $F(n)\ll_\varepsilon n^{4/(9\sqrt{e})+\varepsilon}$ (Balog 1989) |
| Green / Erdős target | every fixed $\varepsilon>0$, unknown |
| ternary smoothness | $\exp\bigl(O(\sqrt{\log n\log\log n})\bigr)$ (Balog–Sárközy / Sárközy) |
| Vinogradov wall for a uniform $n^{o(1)}$ bound | $n(p)\ll_\varepsilon p^{1/(4\sqrt{e})+\varepsilon}$ |

Here $P^+(1)=1$ and
$$
F(n)=\min_{1\le a<n}\max\bigl(P^+(a),P^+(n-a)\bigr),\qquad
G(y)=\min\{n\ge 2:F(n)>y\}.
$$
Green’s “every $n\le N$ is a sum of two $N^\varepsilon$-smooth
integers, for all large $N$” is the uniform statement
$F(n)\le n^\varepsilon$ for large $n$. Isolated values of $G(y)$
are residue unless they force an infinite covering or a new exponent.

Do not claim a table of $G(y)$ as a dent. Do not claim Balog’s
exponent with an implicit $N_0$.

## 2026-08-17 — tonight’s handle

Three live handles, in order of what would count as a dent:

1. **An explicit $\varepsilon<1/2$ with a checkable covering
   template** that writes every $n\ge N_0$ ( $N_0$ explicit) as a
   sum of two $n^\varepsilon$-smooth positive integers, with the
   range $n<N_0$ certified. The square-plus-remainder template is
   $\varepsilon=1/2$ and is not a dent.
2. **A certified finite residue cover** that implies an *infinite*
   statement: a modulus $M$ and, for every class $r\pmod M$, a
   uniform construction (not a lookup table of small $n$) producing
   two $n^\varepsilon$-smooth summands.
3. **A documented obstruction** to any such cover: a verifier that a
   searched family of templates fails, together with the quadratic /
   Fouvry reasons why the search cannot break Balog or the
   Vinogradov wall.

Balog’s own reduction (1989, p.298): it is enough to treat
$N^\alpha$-rough $N$ (least prime factor $>N^\alpha$). If
$N=N'N''$ with $P^+(N')\le N^\alpha<p(N'')$ and
$N''=a+b$ is a good splitting, then $N=N'a+N'b$ is too. Hard
inputs are primes and products of large primes.

Weight he actually uses, for the record (not a template I can
certify without Fouvry):
$$
\omega=u*v*z,\quad
u=\mathbf{1}_{(N^\delta,2N^\delta]},\;
v=\mathbf{1}_{(N^{1/18-\delta},2N^{1/18-\delta}]},\;
z=\mathbf{1}_{\{N^{4/9-2\delta}<h\le 2N^{4/9-2\delta},\;P^+(h)\le N^\alpha\}}.
$$
The exponent $4/(9\sqrt{e})$ is the point where the $z$-sum
$1-\log((4/9)/\alpha)$ stays positive after the Rankin / Mertens
factor $e^{-1/2}$ hidden in Fouvry’s range.

## 2026-08-17 — trivial covering, recorded so I do not claim it

Let $m=\lfloor\sqrt n\rfloor$ and $r=n-m^2$, so $0\le r\le 2m$.
If $r\ge 1$ then $n=m^2+r$ with $P^+(m^2)=P^+(m)\le m\le\sqrt n$
and $P^+(r)\le r\le 2m<2\sqrt n+1$. If $r=0$ then
$n=(m-1)^2+(2m-1)$ and $2m-1<2\sqrt n+1$. Hence
$F(n)<2\sqrt n+1$ for every integer $n\ge 2$. This is Balog’s
“almost trivial” $N^{1/2}$ statement, fully explicit. Isolated
improvements of the constant $2$ on a finite range are residue.

## 2026-08-17 — negative-pseudosquare obstruction (to be certified)

A number $m\equiv 7\pmod 8$ for which $(-m/q)=1$ for every odd
prime $q\le y$ cannot be a sum of two positive $y$-smooth
integers. Proof is elementary Jacobi / quadratic reciprocity and
will be checked, not trusted from the July working report on #334.
Consequence: $G(y)\le A045535(\pi(y)-1)$, and for primes
$p\equiv 3\pmod 4$ one has $n(p)\le F(p)$. A uniform bound
$F(n)\le n^{0.1}$ would beat Burgess on that prime class.

Next: write verifiers and a residue-cover search. The search
product is a failure with a checker, unless a template actually
lifts.

## 2026-08-17 — trivial covering certified, not claimed

`compute/trivial_cover.py`: $F(n)<2\sqrt n+1$ on $[2,200000]$ with
zero failures; worst ratio $F_{\mathrm{split}}/\sqrt n=1.9977$ at
$n=197136$. Large spot checks at $10^{12}$, $10^{18}+3$,
$99991^2$, and $131486759$ all pass. This is the square-plus-remainder
template. It is not a dent.

## 2026-08-17 — obstruction lemma, certified

`compute/obstruction.py`:

- A045535 prefix through $n=22$: every listed $m$ is $7\pmod 8$
  and $(-m/q)=1$ for the first $n$ odd primes. Leastness checked
  through $m\le 10^7$.
- For $M=131486759$, explicit square roots of $-M$ modulo every
  odd prime $q\le 79$. Two-pointer: $M\notin S_{79}+S_{79}$.
  Displayed splitting $649+131486110$ gives $F(M)=83$.
- Smooth counts through $M$: $\lvert S_{73}\cap[1,M]\rvert=727473$,
  $\lvert S_{79}\cap[1,M]\rvert=808372$. Later matched the C bitset
  generator exactly.

The reciprocity argument (even summand $2^k A$, odd summand $B$,
Jacobi symbols of $-M$ on $A$ and $B$, then quadratic reciprocity
forces a sign $-1$ when $M\equiv 7\pmod 8$) was rechecked on every
small A045535 value by a direct search for a forbidden splitting: none
exists.

## 2026-08-17 — residue-cover search, failed

`compute/covering_search.py` on $[2,50000]$ and refined on
$[2,80000]$:

- Short-interval template of length $n^\alpha$: $\alpha=1/2$ has
  only the tiny holes $\{2,3,7,8,23,24\}$ (of which $2,3$ are
  $n^\alpha<2$ artefacts). $\alpha=0.4$ still has 110 holes, last
  at $3496$. $\alpha=1/3$ has thousands.
- Window $2\sqrt n+1$: zero holes, as the trivial covering predicts.
- Finite shift lists on residue classes modulo $8,24,120$: at
  $\alpha=0.4$, modulo $8$, seven classes lift on $[2,20000]$
  and class $5$ dies at $n=18181$. At $\alpha=1/3$ every class
  dies. A fixed list of offsets cannot track a growing smoothness
  bound.
- Square-adjustment $n=(m-k)^2+(n-(m-k)^2)$ with $k\le 256$ and
  $\alpha=0.4$: 309 holes remaining, last still at $79922$. The
  template does not close.
- Even reduction $F(n)\le\max(2,F(\mathrm{odd\ part}(n)))$ is an
  identity and does not remove the odd obstruction.

No finite residue cover lifted. Search residue, as required.

## 2026-08-17 — certified $G(y)$ through $79$

C word-bitset (`g_of_y.c`) independently reproduces A062241:

| $y$ | $G(y)$ | $\lvert S_y\rvert$ through $G(y)$ |
| --- | --- | --- |
| 31 | 118271 | 6598 |
| 37, 41 | 366791 | 13354 / 15343 |
| 43, 47, 53 | 2155919 | 42095 / 48274 / 54486 |
| 59, 61 | 6077111 | 102546 / 114680 |
| 67 | 98538359 | 501974 |
| 71 | 120293879 | 621781 |
| 73 | 131486759 | 727473 |
| 79 | 131486759 | 808372 |

Every integer in $[2,G(y)-1]$ is a sum of two $y$-smooth
positives; $G(y)$ itself is not. This is a finite table.

## 2026-08-17 — exact exception prefixes, still residue

Integer tests $F^q>n^p$, C sweep plus Python recomputation of every
listed $F$:

- $F(n)\le n^{1/2}$ on $[2,10^6]$ except $\{3,7,23\}$.
- $F(n)\le n^{2/5}$ on $[2,10^6]$ except sixteen values, last
  $479=G(11)$.
- $F(n)\le n^{1/3}$ on $[2,3\cdot 10^5]$ except seventy-six
  values, last $18191=G(23)$.

The $n^{0.27}$ sweep (just above Balog) still has exceptions at the
right endpoint of $[2,2\cdot 10^5]$. A last-exception on a prefix
is not $N_0(\varepsilon)$ for Balog's theorem.

The published record is not beaten. Documented residue.

## 2026-08-27 — literature fetched again before q1

Opened, in order, before any q1 search:

- Green, *100 Open Problems*, Problem 59, from
  https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf
  (Dec 2025 text). Still the Balog exponent $4/(9\sqrt{e})\approx 0.2695$,
  still the Wooley / Vinogradov wall at $1/(4\sqrt{e})\approx 0.1516$,
  still a pointer to Erdős #334. No update since the 17 August fetch.
- [Erdős Problem #334](https://www.erdosproblems.com/334) live page
  is behind Cloudflare here. Wayback
  `https://web.archive.org/web/20260824194602/https://www.erdosproblems.com/334`
  (captured 24 August 2026): **OPEN**, “cannot be resolved with a
  finite computation”, last edited 03 April 2026, zero claimed proofs,
  two comments. Statement and Balog exponent unchanged.
- Wayback forum thread, same date: my99n (03 Mar 2026) on A062241
  versus A045535; Woett (19 Nov 2025) on the ternary Sárközy bound,
  the $n^{0.1}$ Vinogradov obstruction, and Erdős’s
  $\exp(c\sqrt{\log n\log\log n})$ binary conjecture.
- OEIS A062241 and A045535 via `scripts/oeis_lookup.py`. Terms match
  the certified $G(y)$ table. A062241 still ends at $a(29)=2570169839$
  in the JSON prefix we received.
- Hildebrand–Tenenbaum, J. Théor. Nombres Bordeaux 5 (1993),
  PDF from https://jtnb.centre-mersenne.org/item/10.5802/jtnb.101.pdf,
  journal pp. 468–469: Balog–Sárközy 1984b give $N^{2/5}$; Balog 1989
  improves to $0.2695$; $N^\varepsilon$ unknown for any fixed
  $\varepsilon>0$. Ternary: $\exp(c\sqrt{\log N\log\log N})$.
- arXiv:2006.15307 (Győry–Hajdu–Sárközy): decomposability of the
  *set* of smooth numbers, not an all-integers binary exponent.
- arXiv:2111.01601v5 (Blomer–Grimmelt–Li–Rydin Myerson): prime plus
  two almost-prime squares; not two smooth summands.
- arXiv:1912.11546v2 (Dimitrov–Vigneri–Attias): RSA / anti-Goldbach
  heuristic, not a theorem.
- Ki–Maier–Sankaranarayanan, Acta Arith. 175.4 (2016): cites Balog
  $0.2695$ as the all-integers binary record; their own theorems are
  square-plus-smooth and prime-plus-smooth almost-all results.
  They also record Balog–Sárközy’s exponential-sum remark that $2/5$
  can be lowered to $0.392$, still above Balog 1989.
- Balog’s publication list
  https://www.renyi.hu/~balog/publist.pdf : item [24] is the 1989
  paper; items [9]–[10] are the 1984 Studia I/II pair.

Published record unchanged. Still no later all-integers binary
exponent. Scoped miss, not a proof that none exists.

## 2026-08-27 — parent replay

Started `python3 compute/verify_all.py` before any q1 search.
Trivial covering and the obstruction lemma replayed immediately.
The Python $G(y)$ bitset matched the published table through
$y=53$. The $y=59$ and $y=61$ rows ($G=6077111$) are the slow
pure-Python bitset; those values were already certified by the C
program in `certs/g_certified.json`. The parent covering-search
script runs after $G$.

## 2026-08-27 — closed-form templates, all fail below $1/2$

New code in `compute/q1/`. Integer tests $F_{\mathrm{template}}^q>n^p$
on $[2,20000]$:

| template | $9/20$ holes | $2/5$ | $1/3$ | $27/100$ | last hole at $2/5$ |
| --- | --- | --- | --- | --- | --- |
| square-plus-remainder | 7081 | 10053 | 13646 | 16950 | 19999 |
| largest power of two | 12737 | 14602 | 16708 | 18287 | 20000 |
| triangular | 12272 | 14613 | 17731 | 19523 | 20000 |
| cube | 9316 | 11375 | 14094 | 17360 | 20000 |
| floor-divisor | 6034 | 9585 | 14244 | 17848 | 19968 |

Holes persist to the right endpoint at every exponent below $1/2$.
The square formula has zero failures of the *true* trivial bound
$F_{\mathrm{split}}<2\sqrt n+1$ on this range, as it must.

Floor-divisor is the closed-form short-interval rewrite: $u=\lfloor n^{p/q}\rfloor$,
$a=n-(n\bmod u)$. The remainder is automatically $n^{p/q}$-smooth by
size. The first summand fails exactly when $\lfloor n/u\rfloor$ is
$n^{p/q}$-rough. At $\varepsilon=1/2$ this is the trivial covering
again. Below $1/2$ it does not lift.

## 2026-08-27 — infinite failure families

`compute/q1/certs/infinite_family.json`:

- Floor-divisor, 129 primes $11\le P\le 541$ and $10000\le P\le 10300$,
  at $2/5$, $1/3$, and $27/100$: a $u$ near $P^{\varepsilon/(1-\varepsilon)}$
  makes $n=Pu+1$ fail the template, 129/129 hits, zero misses. The
  inequality $P>n^\varepsilon$ for this shape is exactly $\varepsilon<1/2$.
  Large sample at $2/5$: $P=10289$, $n=4455138$.
- Largest power of two, $k=4,\ldots,16$: $n=2^k+q$ with $q$ the next
  prime after $2^{k-1}$ fails even $n^{1/2}$ (so fails every smaller
  exponent). Example $k=16$: $n=98307=65536+32771$.

These kill those two formulas as infinite coverings. They are not a
lower bound on $F$.

## 2026-08-27 — polynomial size obstruction

`compute/q1/certs/poly_obstruction.json`. For each of
$x^2$, $x^3$, $x(x+1)$, $x(x+1)/2$, $x^2+x+1$, $x(x+1)(x+2)/6$,
the gap $P(k+1)-P(k)$ at $k\in\{20,50,100,200,400\}$ is at least
$k^{d-1}/2$. Remainder-by-size therefore has exponent $1-1/d\ge 1/2$.
Cubes are worse than squares. Smoothness of a large remainder is the
square-adjustment search already run on 17 August, which left holes.

## 2026-08-27 — two-factor search, same prefixes as $F$

Balog–Sárközy shape: $a=uv$ with $u\le n^{1/5}$ and both $v$ and
$n-a$ equal to $n^{p/q}$-smooth. On $[2,20000]$ this matches $F$
exactly:

- $2/5$: sixteen holes, last $479$, equal to the known $F$ exceptions.
- $1/3$: seventy-six holes, last $18191$, equal to the known $F$
  exceptions.

The $n^{1/5}$ factor restriction does not lose a splitting on this
range. It also does not produce $N_0$. A last exception on a prefix
is not Balog–Sárközy made effective.

No dent. Published record not beaten.


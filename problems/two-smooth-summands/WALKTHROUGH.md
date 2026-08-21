# How the two-smooth-summands search came together

## 0. What was actually missing

The missing object was not another table of the first $n$ that
fails to be a sum of two $y$-smooth numbers. That table is OEIS
A062241, it is finite for each fixed $y$, and Green and Bloom both
warn that the uniform statement cannot be settled by a finite
computation.

What would have counted is a *template that lifts*: a finite list of
residue classes, or an explicit arithmetic construction depending on
$n$ in a checkable way, that writes every large $n$ as
$a+b$ with $P^+(ab)\le n^\varepsilon$ for some
$\varepsilon<1/2$. Isolated prefixes — even a prefix on which
$F(n)\le n^{2/5}$ has only sixteen exceptions — are an incomplete search unless
the template continues.

The analytic gap is the same object Balog named in 1989: positivity
of the binary smooth convolution
$$
R_y(N)=\sum_{a=1}^{N-1}\mathbf{1}_{P^+(a)\le y}\,\mathbf{1}_{P^+(N-a)\le y}
$$
at $y=N^\varepsilon$, uniformly in $N$. Fouvry's large-modulus
theorem gets him down to $4/(9\sqrt e)$. A covering search cannot
replace that input.

## 1. Named false starts, with the specific obstruction

**Square-plus-remainder as a new bound.** Write
$n=m^2+r$ with $0\le r\le 2m$, or $(m-1)^2+(2m-1)$ when $n$
is square. Then $F(n)<2\sqrt n+1$ for every $n\ge 2$. The
verifier in `trivial_cover.py` confirms this on $[2,2\cdot 10^5]$
and on several $10^{12}$–$10^{18}$ spots. Balog's first page
already calls the $N^{1/2}$ statement “almost trivially true.” The
obstruction is not mathematical; it is bibliographic. This is the
covering we were told not to claim.

**A fixed list of shifts, one per residue class.** For each
$r\pmod M$ try the first forty $M$-smooth offsets $a$ and ask
whether $n-a$ is $n^\alpha$-smooth. Modulo $8$ at
$\alpha=0.4$ this almost works on $[2,20000]$: seven classes
lift and class $5$ dies at $n=18181$. At $\alpha=1/3$ every
class dies, the first deaths sitting between $937$ and $4282$.
A fixed offset cannot follow a smoothness bound that grows with
$n$. That is the obstruction.

**Square-adjustment.** Replace $m=\lfloor\sqrt n\rfloor$ by
$m-k$ for $k\le 256$ and demand both $m-k$ and
$n-(m-k)^2$ be $n^{0.4}$-smooth. Three hundred and nine holes
remain on $[2,80000]$, the last at $79922$. Making the first
summand a nearby square of a smooth integer does not buy an
exponent below $1/2$.

**Even reduction.** If $m=a+b$ then $2m=(2a)+(2b)$, so
$F(n)\le\max(2,F(\mathrm{odd\ part}(n)))$. The identity is correct
and useless: the hard $n$ are odd, and the negative-pseudosquare
construction lives in the class $7\pmod 8$.

**Short intervals of length $n^\alpha$ as a proof of
$F(n)\le n^\alpha$.** This *would* lift if every interval
$(n-n^\alpha,n)$ contained an $n^\alpha$-smooth integer. For
$\alpha=1/2$ the only genuine holes on $[2,10^6]$ are
$n=7,8,23,24$, and $F$ itself exceeds $\sqrt n$ only at
$3,7,23$. For $\alpha=0.4$ the short-interval holes run up to
$3496$; two large summands still save those $n$ as soon as one
computes $F$, but the short-interval *template* does not cover
them. Unconditionally, the literature (Balog 1987, Harman,
Matomäki) gives $x^\varepsilon$-smooth numbers in intervals of
length $\sqrt x$, which again returns $F(n)\le\sqrt n$, not a
new exponent.

## 2. The useful failure

The residue-class search dying at a single class modulo $8$ looked,
for a moment, like a near-cover. It taught the opposite lesson. The
seven live classes were live because a short list of small smooth
offsets happened to hit an $n^{0.4}$-smooth complement on a short
prefix. Class $5$ is not arithmetically special; it is the first
place the same finite list ran out of luck. Lengthening the list, or
the modulus, only postpones the first death. Smoothness is a
multiplicative monoid. A finite set of additive residue templates
cannot manufacture two large smooth summands for every $n$.

The same failure, read against Balog's reduction, is sharper. Balog
splits off the $N^\alpha$-smooth kernel of $N$ and reduces to
$N^\alpha$-rough $N$ — primes and products of large primes. Those
are exactly the inputs a small-shift cover never sees: the complement
$n-a$ is then comparable to $n$, and asking it to be
$n^\alpha$-smooth *is* the original problem.

## 3. The click

The click was not a cover. It was the realisation that the
negative-pseudosquare obstruction, which is the only infinite local
obstruction we can write down, is too weak to produce
$F(n)>n^{2/5}$ past a few hundred, and too strong to let any
cover we can certify go below the Burgess exponent.

If $m\equiv 7\pmod 8$ and $(-m/q)=1$ for every odd prime
$q\le y$, then $m$ is not a sum of two positive $y$-smooth
integers. The proof is Jacobi symbols plus quadratic reciprocity
on the even and odd summands; it does not use Dirichlet or Linnik.
Consequently $G(y)\le A045535(\pi(y)-1)$, and for primes
$p\equiv 3\pmod 4$ the least quadratic non-residue satisfies
$n(p)\le F(p)$. A uniform bound $F(n)\le n^{0.1}$ would beat
Burgess on that prime class. That is Green's / Wooley's wall, and
it is real.

But the same construction, evaluated at the certified points, gives
$F(131486759)=83$ while $131486759^{2/5}\approx 1585$. The
obstruction forbids $y=79$, not $y=n^{2/5}$. Along the
A062241 sequence the inequality $F(G(y))>G(y)^{2/5}$ holds for
the first few terms and then flips: $F(1559)=17<1559^{2/5}\approx 18.93$.
After that the obstruction no longer produces counterexamples to
$F(n)\le n^{2/5}$. That is why a C sweep of $[2,10^6]$ finds
exactly sixteen exceptions to $F(n)\le n^{2/5}$, the last at
$n=479=G(11)$, and why the same sweep at exponent $0.27$ still
has exceptions at the right endpoint of $[2,2\cdot 10^5]$.

So the cover we wanted — a finite residue recipe for some
$\varepsilon<1/2$ — is blocked from below by the trivial square
template and from above by Fouvry. The obstruction explains why
$\varepsilon=0.1$ is hopeless and why $\varepsilon=2/5$ can
look finite-exception on a long prefix without being a theorem we
proved.

## 4. The argument, in the order it was found

Green #59 and Bloom #334 were fetched first. The live Bloom page
(edited 03 April 2026) still states Balog's exponent and the
$n^{o(1)}$ conjecture; two comments add the A045535 comparison
and the Vinogradov wall. Balog's five-page paper was fetched next.
The first paragraph contains the two sentences that organised the
night: $N^{1/2}$ is almost trivial, and the method cannot reach
$N^\varepsilon$.

The trivial covering was written down and certified so it could not
be “discovered” later. Then the Jacobi obstruction was proved from
scratch and run against every small negative pseudosquare, and
against $M=131486759$ with displayed roots and a two-pointer
non-representation test. That gave the exact value $F(M)=83$.

Only then did the cover search run. Fixed shifts, square
adjustments, short intervals, and the even reduction were each given
a verifier and each produced holes. The useful picture was the
exception sweep with *integer* tests $F^2>n$, $F^5>n^2$,
$F^3>n$: floating-point $\mathtt{pow}$ had falsely flagged the
cubes $8,27,125$ as $n^{1/3}$ exceptions. The exact lists are
finite on the computed prefixes and stop at values of $G(y)$.

In parallel the C bitset independently reproduced A062241 through
$y=79$. The 73-smooth and 79-smooth counts through $M$ agreed
with the Python generator to the integer. That is a finite
certificate, not a new bound.

## 5. Computer search

Stored under `compute/certs/`.

- `trivial_cover.json` — square template, zero failures on the
  stated range.
- `obstruction.json` — A045535 prefix, roots of $-M$, 
  $F(M)=83$, smooth counts.
- `g_certified.json` — $G(y)$ through $y=79$, C bitset plus
  two-pointer.
- `covering_search.json` and `covering_refined.json` — holes for
  every finite template that was tried.
- `f_exceptions_exact.json` — the sixteen $n^{2/5}$ exceptions
  and the seventy-six $n^{1/3}$ exceptions, each with an explicit
  splitting that realises $F(n)$.

Figures: `figures/g_of_y.png`, `figures/exceptions_two_fifths.png`.

The bitset that certifies $G(73)=131486759$ ORs the 73-smooth
characteristic vector, shifted by each of the $22176$ 73-smooth
integers up to $200000$, and finds no hole in $[2,M-1]$. The
same $M$ has no 79-smooth splitting.

## 6. What is proved vs still open

Proved tonight, all checkable:

- $F(n)<2\sqrt n+1$ for every $n\ge 2$ (elementary; the
  computer only audits).
- The negative-pseudosquare lemma, and $F(131486759)=83$.
- $G(y)$ for every prime $y\le 79$, matching A062241.
- $F(n)\le\sqrt n$ on $[2,10^6]$ except $\{3,7,23\}$.
- $F(n)\le n^{2/5}$ on $[2,10^6]$ except sixteen explicit $n$,
  last $479$.
- $F(n)\le n^{1/3}$ on $[2,3\cdot 10^5]$ except seventy-six
  explicit $n$, last $18191$.
- Every finite residue / shift / square-adjustment template we ran
  fails to cover $\mathbb Z$ at any $\varepsilon<1/2$.

Still open, and not touched:

- $F(n)\le n^\varepsilon$ for a fixed $\varepsilon<4/(9\sqrt e)$
  and all large $n$.
- An effective $N_0(\varepsilon)$ for Balog 1989.
- The conjectured $F(n)\le n^{o(1)}$, equivalently Green #59 for
  every $\varepsilon>0$.
- Whether the sixteen $n^{2/5}$ exceptions are the only ones in
  $\mathbb N$. The prefix is not a proof.

We did not beat the published record. A failed search with a
verifier is the product.

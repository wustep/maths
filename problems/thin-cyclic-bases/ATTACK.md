# Attack log — thin cyclic additive bases (Green 100 #33)

## 2026-08-17 — literature (start with Green #33)

Fetched, in order:

- Green, *100 Open Problems* (Dec 2025 update), Problem 33:
  infinitely many $q$ with $A\subset\mathbb Z/q\mathbb Z$,
  $|A|=(\sqrt2+o(1))q^{1/2}$, and $A+A=\mathbb Z/q\mathbb Z$?
  Comment: “Potentially yes, but I’m not sure I know how to construct
  such sets.” Same question with $q=p$ prime. Then
  $S=\{(x,x^2):x\in A\}\cup\{(1,0)\}$ determines a line in every
  direction in $\mathbb F_p^2$. Counting forbids anything smaller
  than $(\sqrt2+o(1))p^{1/2}$. Asked by Granville (Croot–Lev,
  Problem 5.2) and Caprace–de la Harpe, Question 6.1 (arxiv numbering
  5.e / the $n_p$ estimate).

- Croot–Lev, *Open problems in additive combinatorics*, CRM 43
  (2007), Problem 5.2: smallest $E\subset\mathbb F^r$ determining
  every direction. Counting $|E|\ge\sqrt2\,q^{(r-1)/2}$. Konyagin:
  a difference basis $D\subset\mathbb F^{r-1}$ of size $C q^{(r-1)/2}$
  gives $D\oplus\{0,1\}$ of size $2C q^{(r-1)/2}$. Constant factor
  only.

- Caprace–de la Harpe, arXiv:1807.04992 / Confluentes Math. 12
  (2020): $n_p=\alpha(p,1)$ is the least size of $F\subset\mathbb F_p^2$
  whose difference set meets every line through the origin.
  $n_p>\sqrt{2p}$, and Fitch–Jamison give $n_p\le 2\lceil\sqrt p\rceil+1$.
  Exact value open. Green is the one who pointed them at Croot–Lev.

- Terminology: a *sum cover* of $G$ is $A$ with $A+A=G$
  (Haanpää, J. Integer Seq. 7 (2004), #04.2.6). Equivalently
  $\varphi(G,2)$ in Bajnok, *Additive Combinatorics: A Menu of
  Research Problems* (arXiv:1705.07444 / CRC 2018), and $\mathrm{SS}(n,2)$
  in Bevan–Erskine–Lewis, arXiv:1506.04962.
  Bajnok’s identity: $\varphi(G,2)=\varphi(G,[0,2])+1$.

Counting (absolute, every $n$):

$$
n\le\binom{|A|+1}{2}\implies |A|\ge\frac{-1+\sqrt{1+8n}}{2}=(\sqrt2+o(1))\sqrt n.
$$

No perfect sum cover for $|A|\ge3$ (Haanpää Thm 2.2; Bajnok Thm B.8
for the $[0,2]$-form).

Published upper bounds I must beat or match with a new family:

| quantity | published | source |
| --- | --- | --- |
| all large $n$: $\varphi(\mathbb Z_n,[0,2])$ | any $c_2>\sqrt3\approx1.732$ | Jia–Shen, SIDMA 31 (2017), 796–804 |
| all $n$: elementary | $<2\sqrt n$ | two APs / base-$\lceil\sqrt n\rceil$ digits |
| infinitely many $n$: $\mathrm{SS}(n,2)/\sqrt n$ | $\le\sqrt{8/3}\approx1.63299$ | Bevan–Erskine–Lewis 2017, Cor. 18 |
| interval (hence cyclic) Mrose | $\sqrt{3.5}\approx1.871$ | 7-AP template, $n\sim14t^2$ |
| difference cover $\Delta[\mathbb Z_n]/\sqrt n$ | $\to1$ along Singer / Bose | Banakh–Gavrylkiv arXiv:1702.02631 |
| small-$n$ tables | cyclic sum covers through $n=67$ at size 13; all abelian through 85 | Haanpää 2004; Fitch–Jamison through 54 |

Singer difference sets give $A-A=G$ at size $(1+o(1))\sqrt n$, not
$A+A=G$. A symmetric Singer set of size $k>5$ is impossible
($k(k+1)/2<k(k-1)+1$). Converting a difference cover by
$A\mapsto A\cup(-A)$ costs a factor 2 and lands at the elementary
constant, not below $\sqrt{8/3}$.

Haanpää $n'_s(k)$ (largest cyclic order with a $k$-element sum
cover): 3,5,9,13,19,21,30,35,43,51,63,67 for $k=2,\ldots,13$.
Ratios $k/\sqrt n$ sit in $1.33$–$1.59$. Isolated small-$q$
tables are residue unless they imply an infinite family (house rule).

Green still open as of the Dec 2025 update. No later paper found
that beats BEL’s $\sqrt{8/3}$ for infinitely many $n$, or
Jia–Shen’s $\sqrt3+\varepsilon$ for all large $n$.

Tonight’s dent, in order:

1. An infinite parametric family with
   $|A|\le(c+o(1))\sqrt q$ and $c<\sqrt{8/3}$.
2. The Green constant $c=\sqrt2$.
3. A certified finite $q$ beating a *published asymptotic
   density*, not just Haanpää’s table.

Do not claim a dent from a handful of small-$q$ optima.

## 2026-08-17 — handle

BEL’s $\sqrt{8/3}$ is a 4-family product: $\mathbb Z_{r_1}\times\mathbb Z_{r_2}\times\mathbb Z_6$
with a 4-element strict sum cover $\{0,1,2,4\}$ of $\mathbb Z/6\mathbb Z$,
order $6q^2$, degree $4q+O(1)$. Observation 11 of that paper
caps this *class* at $n\le(3/8)d^2$. Beating $\sqrt{8/3}$
needs a different template.

Candidates:

- three APs $I\cup dI\cup eI$ whose three rectangles tile more
  than $3.375\,\ell^2$ of $\mathbb Z/n\mathbb Z$;
- Singer / Bose Sidon set plus a short repair set of size
  $\ge(\sqrt2-1)\sqrt n$;
- a 2-parameter algebraic family (quadratic window, discrete
  log of an interval, planar-function graph projected to a
  cyclic coordinate).

## 2026-08-17 — BEL replayed

Implemented Bevan–Erskine–Lewis Theorem 10(a) in the product group
$T=\mathbb Z_q\times\mathbb Z_{q-2}\times\mathbb Z_6$, $q\equiv1\pmod6$,
$q\ge7$, then CRT-embedded into $\mathbb Z_n$ with
$n=6q(q-2)$. Connection set from Theorem 9 with
$B=\{0,1,2,4\}$, $c_o=q+2$, $c_u=q$. $A=X\cup\{0\}$ has
size $4q$. Product-group coverage and the independent cyclic
verifier both pass for

| q | n | \|A\| | \|A\|/√n |
| ---: | ---: | ---: | ---: |
| 7 | 210 | 28 | 1.932 |
| 13 | 858 | 52 | 1.775 |
| 19 | 1938 | 76 | 1.726 |
| 31 | 5394 | 124 | 1.688 |
| 37 | 7770 | 148 | 1.679 |
| 43 | 10578 | 172 | 1.672 |
| 61 | 21594 | 244 | 1.660 |

Ratios fall toward $\sqrt{8/3}\approx1.633$. Greedy deletion drops
**zero** points on the $q=13$ and $q=19$ certificates. The
construction is rigid at these orders. This is the published infinite
family, not a dent.

Haanpää 2004 Table 3 (cyclic rows, $n\le67$) independently
re-verified. Those ratios sit in $1.15$–$1.59$. Isolated small
$n$, residue.

## 2026-08-17 — named failures

1. **Equal-length 3-AP $I\cup dI\cup eI$.** Linear coefficient scan:
   $n=A\ell^2+B\ell+C$ for $A\in\{3,4,5\}$, $B\in[-4,4]$,
   $C\in[-3,3]$, differences linear in $\ell$. 56,700 formulas,
   required a cover on $\ell=6,7,8$ simultaneously, **0 hits**.
   Wider $(d,e)$ scan for each $\ell=5,\ldots,12$ in the window
   $3.375\ell^2\le n\le\binom{3\ell+1}{2}$ also **0 hits**.
   Three equal APs do not reach below BEL in this window.

2. **Singer difference set as a Sidon seed.** Corrected
   $\mathrm{Tr}_{q^3/q}$ construction: $|D|=q+1$, $D-D=G$,
   and $D$ is a sum packing, so
   $|D+D|=(q+1)(q+2)/2$ and the missed set has size
   $q(q-1)/2$. Interval or AP thickenings of length
   $\le(\sqrt{8/3}\sqrt v-|D|)$ never completed. Single-point
   gain on the missed set is only $\sim|D|/2$ (histogram:
   $q=13$, max gain 8 on $|D|=14$). Greedy therefore wants
   $\sim q$ extra points and lands at ratio $\sim1.7$–$1.85$,
   not below BEL, and the added residues have no visible pattern.

3. **Bose Sidon set in $\mathbb Z/(q^2-1)$.** Same picture:
   $|A+A|=q(q+1)/2$, interval/AP repair failed inside the BEL
   budget.

4. **Elementary two-AP prune.** Starting from
   $\{0,\ldots,a-1\}\cup a\{0,\ldots,a-1\}$ with
   $a=\lceil\sqrt n\rceil$, greedy deletion drops 0 or 1 point
   on $n\le210$. The construction is essentially unique-representation
   and cannot be thinned by 18% toward $\sqrt{8/3}$.

5. **Quadratic window / geometric progression in $\mathbb F_p$.**
   Squares of $[0,m)$ plus a short interval cover only 2 of 15
   tested primes, both at ratio $>2$. Geometric progressions
   of counting size cover a constant fraction, not the whole field.

6. **Random-style local search** at sizes between counting and BEL
   for $n=31,57,72$: found covers at $n=31,m=9$ (ratio 1.616)
   and $n=57,m=12$ (ratio 1.589). Both below Haanpää's table
   range only for $n=57$ at a size Haanpää already permits
   ($n'_s(12)=63$). Isolated, not a family.

## 2026-08-17 — why BEL's 3/8 is the wall of this template

A directed diameter-2 generating set in
$\mathbb Z_{r_1}\times\mathbb Z_{r_2}\times\mathbb Z_w$ needs a
strict sum cover $B\subset\mathbb Z_w$ of size $k+2=4$. The
largest such $w$ is 6 (Haanpää: $n'_{ss}(4)=6$, and
$\{0,1,2,4\}$ realises it). Then $n=6r_1r_2$,
$|X|=4r_1-1$, and $r_2\sim r_1$ gives
$n/|X|^2\to3/8$. Larger $B$ with larger $w$ is worse:
$n'_{ss}(5)=9$ gives at most $9/25=0.36<3/8$. Observation 11
of BEL is sharp for this class. Beating $\sqrt{8/3}$ needs a
different coupling (finite-field mixing of the two large
coordinates, or a non-AP seed whose repair tiles the missed
sums). Neither was found.

## 2026-08-17 — residue

No infinite family with $c<\sqrt{8/3}$. No certified $q$
that beats a published *asymptotic* density. Green #33 remains
open. The product is the BEL replay, the Haanpää replay, and
the failed-search log.

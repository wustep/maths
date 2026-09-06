# Walkthrough: Landau 3 / Legendre

## 0. What was actually missing

The missing degree of freedom was not another prime search. It was the small
rounding gap between a recent conditional theorem and the computation spliced
into its proof.

The starting record said $2^{64}$. That had already been superseded by
Sorenson and Webster, who checked the stronger Oppermann conjecture through
$n=7.05\cdot10^{13}$. Chamberland and Straub then combined that computation
with an RH prime-interval theorem and printed the exponent threshold $0.2253$.
Their last decimal was rounded rather than structurally fixed.

## 1. Named false starts

**The $2^{64}$ record extension.** This died on the first paper. A search at
that height could only be an independent replay, not a record improvement.

**The proposed prime-gap equivalence.** The condition

$$
p_{k+1}-p_k<2\sqrt{p_k}
$$

is sufficient for Legendre but is stronger than it. Legendre controls square
intervals, not the gap after every prime in that form.

**The published endpoint from GitHub.** The OLC repository does not contain
detailed worker logs through $7.05\cdot10^{13}$. That made a complete source
replay impossible from the public checkout.

**One row, one interval total.** OLC counters are cumulative inside each
worker file. Treating every row as fresh produced thousands of false invariant
failures. Differencing adjacent rows fixed the model.

**Every numeric file is a worker log.** Including `bench.txt` added 284
diagnostic rows. Restricting the audit to tracked `*.out` blobs removed them.

## 2. The useful failure

The missing production logs still left a finite, checkable statement: exactly
what do the public rows cover?

The answer is five components with four holes. The 322,073 selected rows pass
both cumulative-count and success-bucket checks. Their union stops at
$31{,}894{,}400{,}000{,}352$. This is useful provenance, but it is residue.
It cannot be turned into doubt about data that were never committed.

## 3. The click

Let $N=7.05\cdot10^{13}$ and write the exponent as $2+d$. The finite result
covers $x^{(2+d)/2}<N$. At the exact point where that coverage ends, the RH
inequality becomes one scalar test:

$$
F(d)=\frac{d}{2+d}\log N
-\log\!\left(\frac{44\log N}{25(2+d)}\right)\geq0.
$$

The root is

$$
d=0.22524401991936525179\ldots.
$$

So the clean rational $d=901/4000=0.22525$ lies above the root and below the
published $0.2253$. That was the whole opening.

## 4. The argument

Put $d=901/4000$, $\alpha=2+d$, and $X=N^{2/\alpha}$.
The exact certificate proves $F(d)>0$, with lower margin
$0.0000797000675$. Therefore the Chamberland--Straub RH inequality holds at
$X$.

It also proves $(d/\alpha)\log N>1$. This is precisely the derivative test
showing that $x^{d/2}/\log x$ increases for $x\geq X$. The analytic theorem
therefore covers $X$ and everything above it. Their finite real-$x$
proposition covers everything below $X$.

For any larger exponent $\alpha'=r\alpha$, use $y=x^r$. The lower endpoints
agree, and $x^r+1\leq(x+1)^r$ puts the known $\alpha$ interval inside the
$\alpha'$ interval. Thus the result holds for every
$d\geq901/4000$, still assuming RH.

## 5. Computer search

The network-free replay reports:

| Check | Exact scope | Result |
| --- | --- | --- |
| RH overlap | $d=901/4000$ | lower margin $0.0000797000675$ |
| OLC projection | 2,560 files, 322,073 rows | 5 components, 4 holes |
| Edge slice | 100,000 values of $n$ | 200,000 least-prime witnesses |
| Largest left offset | $n=4{,}294{,}952{,}072$ | $489/4{,}294{,}952{,}072$ |
| Largest right offset | $n=4{,}294{,}923{,}873$ | $479/4{,}294{,}923{,}874$ |

Rust generated the edge witnesses with 128-bit endpoint arithmetic. Python
then recomputed every least prime through a different deterministic base set.
The top-20 table is derived only after those rows pass.

## 6. The q3 false start

The first thought was to print more digits of the q1 root. The old splice
condition changes sign at
$0.22524401991936525179\ldots$, so a nearby rational above that number would
immediately beat $0.22525$.

That would be valid, but it would not use all of the published inequality.
Condition (5) arose by dropping terms from inequality (6), and the paper says
the resulting test is only sufficient. The discarded part is tiny at a
splice near $2.8\cdot10^{12}$, but the remaining q1 margin was tinier.

## 7. The second click

For an exponent $\alpha$ strictly between $2$ and $3$, the third derivative
of $z^\alpha$ is positive. Taylor's theorem therefore supplies a positive
quadratic term:

$$
(x+1)^\alpha-x^\alpha
>\alpha x^{\alpha-1}
+\frac{\alpha(\alpha-1)}2x^{\alpha-2}.
$$

This is exactly the scale needed. At the splice, the correction is about
$2.19\cdot10^{-13}$ relative to the leading term. It outweighs the failure
of the old log test at $d=0.22524401991935$.

## 8. Certifying the retained term

Set $\alpha=2+d$, $X=N^{2/\alpha}$, and $A=X^{d/2}$. The exact certificate
does not approximate either fractional power directly. It proves the coarse
bounds

$$
2\cdot10^{12}<X<2.8\cdot10^{12},\qquad25<A<26
$$

by comparing rational enclosures of logarithms. These bounds give a rational
lower bound on the retained correction. The old condition has a negative
certified log margin, but adding
$\log(1+t)\geq t/(1+t)$ leaves more than
$1.51\cdot10^{-14}$.

The remaining question was whether the improvement survived beyond one
point. Differentiating the strengthened sufficient expression reduces that
question to another sign. Its deliberately coarse rational lower bound is
greater than $1.93$, so the expression increases for every $x\geq X$.

## 9. Proven vs still open

Assuming RH, $0.22524401991935$ is a certified threshold for primes between
consecutive $(2+d)$-powers for every real $x\geq1$. It improves the q1 value
$0.22525$, which had already improved the printed $0.2253$. That is the dent.

The final 100,000 square intervals below $2^{64}$ have an independent
Oppermann replay and a reproducible near-miss table. The public OLC checkout
has an authenticated, clearly bounded residue.

No computation extended the published $7.05\cdot10^{13}$ record. RH was not
proved or removed. The exponent $2$ case, Legendre's conjecture itself,
remains open.

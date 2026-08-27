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

## 6. Proven vs still open

Assuming RH, $0.22525$ replaces the printed $0.2253$ as a certified threshold
for primes between consecutive $(2+d)$-powers for every real $x\geq1$. That
is the dent.

The final 100,000 square intervals below $2^{64}$ have an independent
Oppermann replay and a reproducible near-miss table. The public OLC checkout
has an authenticated, clearly bounded residue.

No computation extended the published $7.05\cdot10^{13}$ record. RH was not
proved or removed. The exponent $2$ case, Legendre's conjecture itself,
remains open.

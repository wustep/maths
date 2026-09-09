# Sets with no unique sum mod p

- Slug: `unique-sum`
- Solver: GPT-5.6 Sol (2026-08-16 and 2026-08-23); GPT-6 Astra (2026-09-09 continuation); Grok 4.6 (2026-09-09 continuation).
- Status: open
- Area: Additive combinatorics
- Sources: Green 100 #27; Bedert, Combinatorica 2024 (arXiv:2303.15134v2); Cao–Yuan, arXiv:2608.06728v1 (Aug 2026); OEIS A398173
- Started: 2026-08-16
- Finite campaign: local exact replay through $p=59$; published table through $p=73$

## In general

A nonempty finite $A\subseteq G$ in an abelian group has a *unique sum* if some
$s\in A+A$ has exactly one representation as an unordered pair $\{a,b\}$
from $A$ (repetition allowed). Equivalently: there exist $a,b\in A$ such
that the only solutions of $x+y=a+b$ in $A\times A$ are the swaps of
$(a,b)$. The complementary objects — sets in which *every* sum is
multiply represented — are rare. For $G=\mathbb{Z}/p\mathbb{Z}$ with $p$
an odd prime, write $m(p)$ for the least cardinality of such an $A$ with
$|A|\ge 2$.

Green's Problem 27 asks for the order of $m(p)$. Unique *differences* are
settled up to a constant ($f(p)=\Theta(\log p)$, Straus / Browkin–Diviš–Schinzel);
unique *sums* are not. Bedert (2023/24) moved the bounds from
$\log p\ll m(p)\ll\sqrt{p}$ to $\omega(p)\log p\le m(p)\ll(\log p)^2$.
Cao–Yuan (arXiv:2608.06728, August 2026) replaced the iterated-log lower
bound by a second logarithm,
$$
\log p\cdot\log\log p\ll m(p)\le\Bigl(\tfrac{1}{2(\log_2 3)^2}+o(1)\Bigr)(\log_2 p)^2,
$$
and checked the headline inequalities in Lean. The gap between
$\log p\log\log p$ and $(\log p)^2$ is still the open problem.

The finite campaign is separate from that asymptotic gap. OEIS A398173 now
records $m(p)$ through $p=73$, including $m(59)=15$ (checked 2026-09-09).
The witnesses in `compute/` match its first 15 terms, and a second,
progression-driven implementation independently excludes every smaller size
through $p=53$. At $p=59$ the same 15-element set still gives the upper
bound, and a completed named-midpoint exclusion now rules out every set of
size at most 14. That is the local equality $m(59)=15$, matching the
published table; it is not an improvement of the record. The precise local
claim is in [`compute/q5/CLAIM.md`](compute/q5/CLAIM.md). The first prime
absent from the published exact table is 79. Extending
the exact table to every prime $p\le 200$, plotting it against $\log p$ and
$(\log p)^2$, and describing the extremal sets remains useful finite work.
A new bound here is a checked table extension, not a new asymptotic.

## Precise statement

Let $p$ be an odd prime and $A\subseteq\mathbb{Z}/p\mathbb{Z}$ with
$|A|\ge 2$. A sum $s\in A+A$ is *unique* if there is exactly one
unordered pair $\{a,b\}$ from $A$ (repetition allowed) with $a+b=s$.
Write $r_A(s)=\#\{(a,b)\in A^2:a+b=s\}$ for the ordered representation
function. Because doubling is injective in $\mathbb{Z}/p\mathbb{Z}$ for
odd $p$, $A$ has no unique sum if and only if
$$
r_A(s)\notin\{1,2\}\qquad\text{for every }s\in\mathbb{Z}/p\mathbb{Z}.
$$
(The value $0$ is allowed: $s$ need not lie in $A+A$.) Then
$$
m(p)=\min\bigl\{|A|:A\subseteq\mathbb{Z}/p\mathbb{Z},\;|A|\ge 2,\;A\text{ has no unique sum}\bigr\}.
$$
The minimum is defined: $A=\mathbb{Z}/p\mathbb{Z}$ works. For $p=2$ the
only two-element set is $\{0,1\}$, and $0+1$ has ordered multiplicity
$2$, so $m(2)$ is undefined; restrict to odd primes.

**Finite subquestion.** Compute the exact integer $m(p)$ for
every prime $3\le p\le 200$. For each such $p$, exhibit at least one
extremal set. Record, for the extremal examples, whether they look like
intervals, like Nedev/Bedert balanced sets, like Cao–Yuan symmetric
squares $C+C$ of a weakly ternary-balanced $C$, or like something
else. Dump a CSV under `compute/` and plot $m(p)$ against $\log p$
and against $(\log p)^2$.

## What a solution looks like

- A CSV `compute/green_m_p.csv` with columns including `p,m,witness` (witness a sorted
  list of residues), independently re-runnable.
- A check that each witness has no unique sum, and that no smaller set
  exists (exhaustive for small $p$; SAT / Z3 / cardinality SAT for the
  rest, with the encoding written down).
- Two figures: $m(p)$ vs $\log p$, and $m(p)$ vs $(\log p)^2$,
  via `/maths/src/maths/figures.py`.
- A short note on extremal shape. Optional Lean: a predicate
  `NoUniqueSum` and a check of one small witness (e.g. $m(5)=4$,
  $A=\{0,1,2,3\}$).
- This does **not** settle Green's #27. Do not claim an asymptotic.

## Related

- [Ben Green, *100 Open Problems*, Problem 27](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Bedert, *On unique sums in Abelian groups*, arXiv:2303.15134](https://arxiv.org/abs/2303.15134) ([Combinatorica 44 (2024)](https://doi.org/10.1007/s00493-023-00069-w))
- [Cao–Yuan, *A second-logarithm lower bound for sets with no unique sums*, arXiv:2608.06728](https://arxiv.org/abs/2608.06728)
- [OEIS A398173](https://oeis.org/A398173) (20 terms, through $p=73$)
- Nedev, *An algorithm for finding a nearly minimal balanced set in $\mathbb{F}_p$*, Math. Comp. 78 (2009)

## Computations

**Finite status (2026-09-09): local exact value matching the record.**
$m(59)=15$. The 15-set is checked in two languages. Every set of size at
most 14 is excluded by the AP5 ceiling together with the 27 AP4-but-not-AP5
named midpoint classes and the 25 AP4-free classes; C and Rust agree on
every class. This matches OEIS A398173 and does not improve it. See
[`compute/q5/CLAIM.md`](compute/q5/CLAIM.md) and
[`compute/q5/run_all.sh`](compute/q5/run_all.sh).

## Figures

Table through $p=53$: [`figures/m_p.png`](figures/m_p.png).

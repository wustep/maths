# Sets with no unique sum mod p

- Slug: `no-unique-sum-mod-p`
- Status: open
- Area: Additive combinatorics
- Sources: Green 100 #27; Bedert, Combinatorica 2024 (arXiv:2303.15134); Cao–Yuan, arXiv:2608.06728 (Aug 2026); OEIS A398173
- Started: 2026-08-16
- Tonight: finite-cex, cost S — exact \(m(p)\) for all primes \(p\le 200\)

## In general

A nonempty finite \(A\subseteq G\) in an abelian group has a *unique sum* if some
\(s\in A+A\) has exactly one representation as an unordered pair \(\{a,b\}\)
from \(A\) (repetition allowed). Equivalently: there exist \(a,b\in A\) such
that the only solutions of \(x+y=a+b\) in \(A\times A\) are the swaps of
\((a,b)\). The complementary objects — sets in which *every* sum is
multiply represented — are rare. For \(G=\mathbb{Z}/p\mathbb{Z}\) with \(p\)
an odd prime, write \(m(p)\) for the least cardinality of such an \(A\) with
\(|A|\ge 2\).

Green's Problem 27 asks for the order of \(m(p)\). Unique *differences* are
settled up to a constant (\(f(p)=\Theta(\log p)\), Straus / Browkin–Diviš–Schinzel);
unique *sums* are not. Bedert (2023/24) moved the bounds from
\(\log p\ll m(p)\ll\sqrt{p}\) to \(\omega(p)\log p\le m(p)\ll(\log p)^2\).
Cao–Yuan (arXiv:2608.06728, August 2026) replaced the iterated-log lower
bound by a second logarithm,
\[
\log p\cdot\log\log p\ll m(p)\le\Bigl(\tfrac{1}{2(\log_2 3)^2}+o(1)\Bigr)(\log_2 p)^2,
\]
and checked the headline inequalities in Lean. The gap between
\(\log p\log\log p\) and \((\log p)^2\) is still the open problem.

Tonight is not that gap. Tonight is the finite table. OEIS A398173 records
\(m(p)\) only through the 14th odd prime (\(p=47\)):
\(3,4,5,7,7,8,9,10,11,11,12,13,13,13\). Extending the table to every prime
\(p\le 200\), plotting it against \(\log p\) and \((\log p)^2\), and writing
down the shape of the extremal sets is a residue the next quest can use.
A dent is a checked table plus a figure, not a new asymptotic.

## Precise statement

Let \(p\) be an odd prime and \(A\subseteq\mathbb{Z}/p\mathbb{Z}\) with
\(|A|\ge 2\). A sum \(s\in A+A\) is *unique* if there is exactly one
unordered pair \(\{a,b\}\) from \(A\) (repetition allowed) with \(a+b=s\).
Write \(r_A(s)=\#\{(a,b)\in A^2:a+b=s\}\) for the ordered representation
function. Because doubling is injective in \(\mathbb{Z}/p\mathbb{Z}\) for
odd \(p\), \(A\) has no unique sum if and only if
\[
r_A(s)\notin\{1,2\}\qquad\text{for every }s\in\mathbb{Z}/p\mathbb{Z}.
\]
(The value \(0\) is allowed: \(s\) need not lie in \(A+A\).) Then
\[
m(p)=\min\bigl\{|A|:A\subseteq\mathbb{Z}/p\mathbb{Z},\;|A|\ge 2,\;A\text{ has no unique sum}\bigr\}.
\]
The minimum is defined: \(A=\mathbb{Z}/p\mathbb{Z}\) works. For \(p=2\) the
only two-element set is \(\{0,1\}\), and \(0+1\) has ordered multiplicity
\(2\), so \(m(2)\) is undefined; restrict to odd primes.

**Tonight's finite subquestion.** Compute the exact integer \(m(p)\) for
every prime \(3\le p\le 200\). For each such \(p\), exhibit at least one
extremal set. Record, for the extremal examples, whether they look like
intervals, like Nedev/Bedert balanced sets, like Cao–Yuan symmetric
squares \(C+C\) of a weakly ternary-balanced \(C\), or like something
else. Dump a CSV under `compute/` and plot \(m(p)\) against \(\log p\)
and against \((\log p)^2\).

## What a solution looks like

- A CSV `compute/m_p.csv` with columns `p,m,witness` (witness a sorted
  list of residues), independently re-runnable.
- A check that each witness has no unique sum, and that no smaller set
  exists (exhaustive for small \(p\); SAT / Z3 / cardinality SAT for the
  rest, with the encoding written down).
- Two figures: \(m(p)\) vs \(\log p\), and \(m(p)\) vs \((\log p)^2\),
  via `/maths/src/maths/figures.py`.
- A short note on extremal shape. Optional Lean: a predicate
  `NoUniqueSum` and a check of one small witness (e.g. \(m(5)=4\),
  \(A=\{0,1,2,3\}\)).
- This does **not** settle Green's #27. Do not claim an asymptotic.

## Related

- [Ben Green, *100 Open Problems*, Problem 27](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Bedert, *On unique sums in Abelian groups*, arXiv:2303.15134](https://arxiv.org/abs/2303.15134) ([Combinatorica 44 (2024)](https://doi.org/10.1007/s00493-023-00069-w))
- [Cao–Yuan, *A second-logarithm lower bound for sets with no unique sums*, arXiv:2608.06728](https://arxiv.org/abs/2608.06728)
- [OEIS A398173](https://oeis.org/A398173) (14 terms, through \(p=47\))
- Nedev, *An algorithm for finding a nearly minimal balanced set in \(\mathbb{F}_p\)*, Math. Comp. 78 (2009)

## Quests so far

- [q1-overnight](quests/q1-overnight.md) — exact \(m(p)\) for \(p\le 200\), table + plots + extremal shape. Status: ready.

## Figures

None yet. The overnight quest should embed `figures/m-vs-log.png` and
`figures/m-vs-log2.png` here.

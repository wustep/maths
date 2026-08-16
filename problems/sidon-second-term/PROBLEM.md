# Sidon second term

- Slug: `sidon-second-term`
- Status: open
- Area: Additive combinatorics
- Sources: Erdős #30; Green 100 #31; Carter–Hunter–O'Bryant, Acta Math. Hungar. 175 (2025) (arXiv:2310.20032)
- Started: 2026-08-16
- Tonight: bound-search, cost M — Sidon search in \([N]\) up to \(N\ge 10^4\), second-term gap plot

## In general

A set \(A\) of integers is *Sidon* if all pairwise sums \(a+b\) with
\(a\le b\) are distinct (equivalently: all differences \(a-b\) for
\(a\ne b\) are distinct). Write \(h(N)\) for the largest Sidon subset
of \(\{1,\dots,N\}\). Singer's perfect difference sets from
\(\mathrm{PG}(2,q)\) give \(h(N)\ge(1-o(1))\sqrt{N}\). Erdős–Turán
(1941) proved \(h(N)\le\sqrt{N}+N^{1/4}+1\). The \(N^{1/4}\)
secondary term has been chipped at: Balogh–Füredi–Roy \(0.998\),
O'Bryant, then Carter–Hunter–O'Bryant (2025)
\[
h(N)\le\sqrt{N}+0.98183\,N^{1/4}+O(1).
\]
Erdős #30 / Green #31 ask whether, for every \(\varepsilon>0\),
\(h(N)=\sqrt{N}+O_\varepsilon(N^\varepsilon)\). Even
\(h(N)=\sqrt{N}+O(1)\) has been suggested and called too optimistic.
Any strict improvement of either side for infinitely many \(N\) is
open. (Later 2026 notes discuss smaller published coefficients;
tonight's benchmark is the \(0.98183\) record named in the quest.)

Tonight is computational Erdős: search Sidon subsets of \([N]\) out
to at least \(10^4\), compare \(|A|\) to \(\sqrt{N}+0.98183\,N^{1/4}\),
plot the second-term gap, and try one modular / Singer-style
construction that beats greedy on some \(N\).

## Precise statement

\(A\subseteq\mathbb{Z}\) is Sidon if \(a+b=c+d\) with \(a\le b\),
\(c\le d\), and \(\{a,b\}=\{c,d\}\) as unordered pairs, whenever
\(a,b,c,d\in A\). Let
\[
h(N)=\max\bigl\{|A|:A\subseteq\{1,\dots,N\}\text{ is Sidon}\bigr\}.
\]
Write \(U(N)=\sqrt{N}+0.98183\,N^{1/4}\) for the Carter–Hunter–O'Bryant
main term (the \(O(1)\) is not in the plot). The *second-term gap* of
a Sidon \(A\subseteq[N]\) is
\[
g(N,A)=U(N)-|A|.
\]
Greedy: start from \(\emptyset\) and repeatedly insert the least
positive integer that preserves the Sidon property, then intersect
with \([N]\). Singer: for a prime power \(q\), a perfect difference
set of size \(q+1\) in \(\mathbb{Z}/(q^2+q+1)\mathbb{Z}\) unwraps to
a Sidon set of size \(q+1\) in an interval of length \(q^2+q+1\).
Bose–Chowla and other modular constructions are allowed.

**Tonight's finite subquestion.** For \(N\) up to at least \(10^4\),
compute greedy \(|A|\), at least one modular/Singer-style \(|A|\),
and (where cheap) an exact or branch-and-bound \(h(N)\) on a
prefix of \(N\). Plot \(g(N,A)\) for these families. Exhibit at
least one \(N\) where a modular/Singer-style construction beats
greedy. Do not claim a new coefficient on \(N^{1/4}\).

## What a solution looks like

- Tables under `compute/` (greedy, Singer/modular, optional exact
  \(h(N)\) on a prefix). Re-runnable Sidon checkers.
- A figure of the second-term gap \(U(N)-|A|\) vs \(N\), via
  `/maths/src/maths/figures.py`.
- One explicit modular/Singer construction that beats greedy on
  some listed \(N\), with both sets written down.
- Optional Lean: the Sidon predicate and a check that a tiny
  Singer unwrap (e.g. \(q=2\) or \(q=3\)) is Sidon.
- This does **not** improve \(0.98183\) and does **not** prove
  Erdős #30.

## Related

- [Erdős Problem #30](https://www.erdosproblems.com/30)
- [Ben Green, *100 Open Problems*, Problem 31](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Carter, Hunter, O'Bryant, *On the diameter of finite Sidon sets*, arXiv:2310.20032](https://arxiv.org/abs/2310.20032) ([Acta Math. Hungar. 175 (2025)](https://doi.org/10.1007/s10474-024-01499-8))
- [O'Bryant, *A complete annotated bibliography of work related to Sidon sequences*](https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS11)
- Singer, *A theorem in finite projective geometry and some applications to number theory*, Trans. Amer. Math. Soc. 43 (1938)

## Quests so far

- [q1-overnight](quests/q1-overnight.md) — Sidon search to \(N\ge 10^4\), gap plot, one modular construction that beats greedy. Status: ready.

## Figures

None yet. The overnight quest should embed `figures/second-term-gap.png` here.

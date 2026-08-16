# Chowla's cosine problem, small n

- Slug: `chowla-cosine`
- Status: open
- Area: Harmonic analysis / additive combinatorics
- Sources: Green 100 #81; Erdős #510; Bedert, arXiv:2509.05260 (2025); Jin–Milojević–Tomon–Zhang, arXiv:2509.03490
- Started: 2026-08-16
- Tonight: bound-search, cost S — certified small-\(n\) minima vs \(\sqrt{n}\) and \(n^{1/7}\)

## In general

For a finite set \(A\) of \(n\) integers, the cosine polynomial
\[
f_A(\theta)=\sum_{a\in A}\cos(2\pi a\theta)
\]
has mean zero and \(f_A(0)=n\), so it must go negative. Chowla asked
how negative: is there an absolute \(c>0\) such that every \(n\)-set
satisfies \(\min_\theta f_A(\theta)\le -c\sqrt{n}\)? That square-root
excursion is still open (Green #81, Erdős #510). Difference sets of
Sidon sets show that \(\sqrt{n}\) is best possible if the conjecture
is true.

The analytic history is long: logarithmic bounds from the Littlewood
\(L^1\) conjecture, then Bourgain, then Ruzsa's
\(\exp(c\sqrt{\log n})\). In September 2025 Bedert proved the first
polynomial bound, \(\min f_A\le -n^{1/7-o(1)}\); independently
Jin–Milojević–Tomon–Zhang obtained a weaker polynomial exponent.
The \(\sqrt{n}\) conjecture is untouched.

Tonight is a Tao-style small-\(n\) plot, not a new exponent.
Compute actual minima on structured \(n\)-sets for \(n\le 16\),
compare them to \(\sqrt{n}\) and to \(n^{1/7}\), and
interval-certify the worst few. The residue is a figure a human
can read.

## Precise statement

For a finite \(A\subset\mathbb{Z}\) write
\[
f_A(\theta)=\sum_{a\in A}\cos(2\pi a\theta),\qquad
K(A)=-\min_{\theta\in\mathbb{R}}f_A(\theta),\qquad
K(n)=\min_{|A|=n}K(A).
\]
(Bedert's \(f_A(x)=\sum\cos(ax)\) on \([0,2\pi]\) is the same function
up to the substitution \(x=2\pi\theta\).) Chowla's conjecture is
\(K(n)\gg\sqrt{n}\). Bedert gives \(K(n)\gg n^{1/7-o(1)}\).

**Tonight's finite subquestion.** For each \(n\le 16\), compute
numerical (then interval-certified) values of \(\min_\theta f_A\) on
a library of structured \(n\)-sets:

- intervals \(\{1,\dots,n\}\) and \(\{0,\dots,n-1\}\)
- Sidon sets in a small interval, and Sidon difference sets \(B-B\)
  when \(|B-B|=n\)
- Bose–Chowla (and Singer, if the parameters fit)
- random \(n\)-subsets of a small universe, many samples
- a *complete* search on a small universe (e.g. all \(n\)-subsets of
  \(\{1,\dots,M\}\) for an \(M\) you can finish; record \(M\))

Plot the recorded minima against \(\sqrt{n}\) and against \(n^{1/7}\).
Interval-certify (mpmath / Arb-style balls, or a rational
trigonometric identity plus a signed evaluation) the worst few
examples — the ones closest to zero, i.e. the apparent extremizers
for \(K(n)\).

## What a solution looks like

- A table `compute/minima.csv` with \(n\), family, set, floating
  \(\min f_A\), and a certified upper bound on that min (so a
  certified lower bound on \(K(A)\)).
- A figure of those values against \(\sqrt{n}\) and \(n^{1/7}\), via
  `/maths/src/maths/figures.py`.
- Interval certificates for the worst few (the least negative
  structured examples, and the complete-search winner on the small
  universe). Scripts under `compute/`, re-runnable.
- Optional Lean: the identity \(f_A(\theta)=\mathrm{Re}\sum e^{2\pi i a\theta}\)
  and a check of one tiny exact evaluation (e.g. \(A=\{1,2,3\}\) at
  a rational \(\theta\)).
- This does **not** improve Bedert's exponent and does **not** prove
  Chowla. Do not claim \(K(n)\gg\sqrt{n}\).

## Related

- [Ben Green, *100 Open Problems*, Problem 81](https://people.maths.ox.ac.uk/greenbj/papers/open-problems.pdf)
- [Erdős Problem #510](https://www.erdosproblems.com/510)
- [Bedert, *Polynomial bounds for the Chowla Cosine Problem*, arXiv:2509.05260](https://arxiv.org/abs/2509.05260)
- [Jin, Milojević, Tomon, Zhang, *From small eigenvalues to large cuts, and Chowla's cosine problem*, arXiv:2509.03490](https://arxiv.org/abs/2509.03490)
- [Open Problem Garden, Chowla's cosine problem](https://www.openproblemgarden.org/op/chowlas_cosine_problem)
- [formal-conjectures, Erdős 510](https://github.com/google-deepmind/formal-conjectures/blob/main/FormalConjectures/ErdosProblems/510.lean)

## Quests so far

- [q1-overnight](quests/q1-overnight.md) — structured + complete small-\(n\) minima, plot vs \(\sqrt{n}\) and \(n^{1/7}\), certify the worst few. Status: ready.

## Figures

None yet. The overnight quest should embed `figures/minima-vs-sqrt-n.png` here.

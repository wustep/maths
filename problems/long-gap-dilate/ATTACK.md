# Attack log — a long gap in a dilate modulo a prime

## 2026-08-17 — literature (do not claim a dent yet)

Fetched:

- Green, *100 Open Problems* (update Dec 2025), Problem 32:
  let \(p\) be prime and \(A\subset\mathbb Z/p\mathbb Z\) of size \(\sqrt p\).
  Is there a dilate of \(A\) with a gap of length \(100\sqrt p\)?
  Comments: Shakan [280] used the polynomial method to replace 100 by 2,
  “but this appears to be the limit of his method”. Variants with
  \(|A|\sim\omega(p)\) recover Szemerédi (\(\omega\sim cp\)) or Dirichlet
  Bohr sets (\(\omega\le c\log p\)). The finite-field model \(\mathbb F_2^n\)
  is easy by averaging. A positive answer would not automatically improve
  Green #31, because it is not known that infinitely many primes admit a
  Sidon set of size \(\sqrt p+O(1)\).

- The list citation `arXiv:2205.14038` / “On higher moments of Fourier
  coefficients” is **wrong**. That id is Jiang–Cai–Wu et al., *Quantum
  Simulation of the Two-Dimensional Weyl Equation* (quant-ph). The paper
  Green actually cites is

  George Shakan, *A large gap in a dilate of a set*,
  [arXiv:2004.14828](https://arxiv.org/abs/2004.14828),
  SIAM J. Discrete Math. 34 (2020), 2553–2555,
  doi:10.1137/20M1335030.

  Theorem 1: if \(|A|>1\), then
  \[
    \sup_{d\in\mathbb F_p^\times} g(d\cdot A)\;\ge\; 2p/|A|-2,
  \]
  equivalently \(L(A)\ge 2(1-|A|/p)\), where \(g\) is the longest run of
  consecutive misses and \(L(A)=(|A|/p)\sup g(dA)\). For \(|A|\sim\sqrt p\)
  this is a gap of \(2\sqrt p-2\). SIAM “Cited By” is empty (accessed
  2026-08-17). No later improvement of the universal leading constant 2
  found.

- Shakan’s argument is Rédei / Alon: \(P=A\times\{1,\ldots,m\}\) meets
  every line \(y=dx+t\) with \(d\ne0\); the vanishing polynomial
  \(w(d,t)=d\prod(b+da+t)\) is \((t^p-t)u+(d^p-d)v\); the top homogeneous
  slice gives \(\chi_A^m=t^p g+h\); then \(\chi_A^{m-1}\) divides the
  Wronskian \(h'g-hg'\) of degree \(\le 2k-1\). The 2 is exactly
  \(\deg g+\deg h\). Green’s “limit of the method” is this degree count:
  at \(m\sim 2p/|A|\) there are no forced middle coefficients. Ordinary
  vs discrete derivatives, or \(\deg W\le 2k-2\) from cancelled leading
  terms, only moves \(O(1)\). Isolated small-\(p\) tables are not a dent
  unless they imply a larger **universal** \(C\).

- Related, not a replacement:
  Di Benedetto–Solymosi–White, arXiv:2001.06994 (Rédei–Szőnyi for
  cartesian products / directions). Korsky, arXiv:2606.01780, hitting
  \(k\)-APs in \([N]\) at \(k=\sqrt N\) (linear interval, not
  \(\mathbb Z/p\mathbb Z\)). Formal-conjectures #1588 is a Lean ticket,
  no mathematics.

Published record I must beat: **Shakan’s universal 2**. A construction
with \(\max_d g(dA)\le(2+\varepsilon)\sqrt p\) would show that 2 cannot
be replaced by \(2+\varepsilon\). A proof that every \(A\) of size
\(\sim\sqrt p\) has some dilate missing \(C\sqrt p\) with a fixed
\(C>2\) is the dent. \(G(p,n):=\min_{|A|=n}\max_d g(dA)\).

## 2026-08-17 — tonight’s handles

1. Re-derive Shakan and see whether the unused interval structure of
   \(B=\{1,\ldots,m\}\) (rising factorials / binomial polynomials)
   improves the Wronskian degree. The written proof uses only that
   \(P\) is a cartesian product.
2. Structure vs randomness: rank-\(O(1)\) GAPs collapse under Dirichlet
   (some dilate sits in an interval of length \(o(p)\)); random / Sidon /
   small multiplicative subgroups should have \(\max g\sim(p/n)\log n\).
   If the minimum really tracks \(\log n\), that is a dent (\(C\to\infty\)).
   If some algebraic family stays at \(C=O(1)\), 2 may be sharp.
3. Exact \(G(p,n)\) for small \(p\) by SAT (hitting all \(T\)-APs) and
   constructions + local search for larger \(p\). Tables are residue
   unless they force a lifting argument.

Starting with (1) and a compute census, then (2).

## 2026-08-17 — dictionary

- \(g(A)\): max \(t\) such that some translate of \(\{1,\ldots,t\}\)
  misses \(A\). Equivalently one less than the longest circular run of
  misses, equivalently the longest arithmetic progression in \(A^c\)
  (any difference) after undoing a dilate.
- \(\max_d g(dA)\) = length of the longest AP contained in \(A^c\).
- Green #32: every \(A\) of size \(\sqrt p\) has \(A^c\) containing an
  AP of length \(100\sqrt p\).
- Shakan: every \(A\) of size \(n>1\) has \(A^c\) containing an AP of
  length \(2p/n-2\).
- Hitting-set dual: \(H(p,T)\) = min size of a set meeting every
  \(T\)-term AP. Shakan \(\Leftrightarrow H(p,T)>2p/(T+2)\). A universal
  \(C>2\) is \(H(p,C\sqrt p)>\sqrt p\).

## 2026-08-17 — dictionary check, then Shakan's 2 is a degree wall

Re-derived the proof. Set \(m=\sup g(dA)+1\), \(B=\{1,\ldots,m\}\),
\(k=nm-p+1\), \(w(d,t)=d\prod_{a,j}(t+j+da)\). Alon gives
\(w=(t^p-t)u+(d^p-d)v\). The top homogeneous slice is
\(\chi^m=t^pg+h\) with \(\deg g,\deg h\le k\). Then
\(\chi^{m-1}\) divides the Wronskian \(W=h'g-hg'\), and
\(\deg W\le 2k-1\). Cancelled leading terms actually give
\(\deg W\le 2k-2\), which only rearranges the \(O(1)\). The comparison
\((m-1)n\le 2k-1\) is exactly \(nm\ge 2p-n-1\).

The 2 is \(\alpha=2\) in \(\deg g+\deg h\le\alpha k\). To get leading
constant \(C\) one needs \(\alpha=C/(C-1)\), so \(C=2.5\) wants
\(\alpha=5/3\) and \(C=3\) wants \(\alpha=3/2\). Nothing in the
homogeneous slice forces that.

Worse: at \(m=Cp/n\) with \(C>2\), one has \(k=(C-1)p+O(1)>p\), so
the “middle coefficients” of \(\chi^m\) that would have to vanish sit
in an empty range. There are **no conditions** for \(C>2\). Green’s
“limit of the method” is this empty middle, not a missing lemma.

The interval structure of \(B\) is thrown away when
\(\prod_j(t+j+da)\) is replaced by \((t+da)^m\). That is the unused
degree of freedom. A direct 2-variable experiment
(`poly_experiment.py`) on \(p=11\), \(A=\{0,1,3\}\) confirms \(w\)
vanishes on \(\mathbb F_p^2\) precisely when \(m>\max_d g(dA)\), as it
must: the full \(w\) restates the hitting condition and does not
improve the degree bound.

If \(0\in A\) (legal by translation), \(\deg_d w=1+(n-1)m\). At the
\(C=2\) scale this is still \(>p\), so the \(d^p-d\) reduction does
not go away.

## 2026-08-17 — Dirichlet / structure-vs-randomness, no √p dent

`max_d g(dA)` is the length of the longest AP in \(A^c\). Equivalently
\(G(p,n)\) is one less than the minimal \(T\) such that some \(n\)-set
hits every \(T\)-AP.

Dirichlet in \(n-1\) simultaneous approximations: some dilate of an
\(n\)-set has circular diameter \(\le n\,p^{1-1/(n-1)}\), hence
\[
  G(p,n)\;\ge\; p-n\,p^{(n-2)/(n-1)}-1.
\]
For each **fixed** \(n\) the right-hand side is \(p-o(p)\) and
\(G(p,n)/(p/n)\to n\). This beats Shakan once \(n=o(\log p/\log\log p)\),
which is Green’s Bohr-set regime already. At \(n\sim\sqrt p\) one has
\(p^{1/\sqrt p}\to 1\) and the diameter bound exceeds \(p\). No
clustering, no dent.

Energy / Freiman: sets with \(|A-A|\le 3n\) are almost APs and have
some dilate with gap \(p-O(n)\), huge. Random sets of size \(\sqrt p\)
have energy \(\sim 2n^2\) and typical max-gap \(\sim(p/n)\log n\),
also huge. The dangerous sets sit in the middle and are exactly the
ones Shakan treats. Rank-2 Bohr sets / GAPs collapse by 2-dimensional
Dirichlet to diameter \(p^{3/4}\), complementary gap \(p-p^{3/4}\),
so they are not extremal for *minimising* \(\max_d g\).

Cauchy–Schwarz on occupancy \(N(d,t)=|dA\cap(t+I)|\) recovers only
the pigeonhole \(C\ge 1\). Inclusion-exclusion with a matching of
pairs recovers only \(C\ge 1+o(1)\).

## 2026-08-17 — exact G, independently checked

SAT encoding: \(A\) has \(\max_d g(dA)<T\) iff \(A\) hits every
\(T\)-AP. Binary search \(T\), symmetry \(0,1\in A\), Glucose4,
cardinality via sequential counters (`sat_exact.py`).

Exact values for \(n=\mathrm{round}\sqrt p\):

| p | n | G | Shakan | G/(p/n) | G/√p |
| --- | --- | --- | --- | --- | --- |
| 17 | 4 | 9 | 6.5 | 2.118 | 2.183 |
| 31 | 6 | 13 | 8.33 | 2.516 | 2.335 |
| 47 | 7 | 18 | 11.43 | 2.681 | 2.626 |
| 53 | 7 | 22 | 13.14 | 2.906 | 3.022 |
| 61 | 8 | 21 | 13.25 | 2.754 | 2.689 |
| 71 | 8 | 26 | 15.75 | 2.930 | 3.086 |

Full table in `compute/certs/sat_G.jsonl`. Every witness recomputed
from scratch (`verify_sat_witnesses.py`). Enumeration of all
\(\{0,1\}\subset A\) agrees through \(p=41\)
(`enum_diagonal.py`). `verify.py` checks Shakan on every nonempty
proper subset of \(\mathbb F_p\) for \(p\le 13\).

Fixed-\(n\) enumerations: \(G(p,3)/(p/3)\) climbs from 1.2 to 2.76
at \(p=199\), consistent with Dirichlet \(\to 3\). \(G(p,4)/(p/4)\)
reaches 2.97 at \(p=97\). Extra \(G-(2p/n-2)\) on the diagonal is
order \(n\), which *would* be a leading-constant 3 if it persisted,
and would be \(O(1)\) slack if it died. The table does not decide.

## 2026-08-17 — constructions are not a 2+o(1) family

Local search upper bounds on \(G\) sit at ratio \(3.0\)–\(3.5\) for
\(p\le 113\), slightly above the SAT values where both exist.
Random / geometric / jittered / equally-spaced all have some dilate
that clusters (equally-spaced collapses to an interval). Multiplicative
subgroups of size \(\sim\sqrt p\) look random-like additively and
have large max-gap. Singer difference sets (prime \(q\),
\(p=q^2+q+1\)) *match* SAT \(G\) at \(p=13,31\), then at \(q=17\),
\(p=307\), \(n=18\) give \(g=90\), ratio \(5.28\). Not a \(C\to 2\)
family.

Greedy hitting sets for \(T=2\sqrt p\) need more than \(\sqrt p\)
vertices, as Shakan requires. For \(T=3\sqrt p\) greedy is sometimes
at most \(\sqrt p\), sometimes not, and is suboptimal versus SAT.

## 2026-08-17 — stop

No proof that every \(A\) of size \(\sim\sqrt p\) has a dilate
missing \(C\sqrt p\) with a fixed \(C>2\). No infinite family with
\(\max_d g\le(2+\varepsilon)\sqrt p\). Shakan’s 2 is still the
published universal leading constant. The SAT table and the failed
homogeneous / Dirichlet / energy / CS attempts are the residue.
The interval structure of \(B\) remains the live handle, unused.

# A long gap in a dilate modulo a prime

- Slug: `long-gap-dilate`
- List: P08
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Additive combinatorics
- Sources: Green 100 #32; Shakan, SIAM J. Discrete Math. 34 (2020),
  arXiv:2004.14828 (the list id `arXiv:2205.14038` is a different paper)
- Started: 2026-08-17

## Statement

Let \(p\) be prime and \(A\subset\mathbb Z/p\mathbb Z\). Write \(g(A)\)
for the longest run of consecutive residues missed by \(A\), and
\(d\cdot A=\{da:a\in A\}\). Green #32: if \(|A|=\sqrt p\), is there a
dilate with \(g(d\cdot A)\ge 100\sqrt p\)?

Shakan (2020): for every \(A\) with \(|A|>1\),
\[
  \sup_{d\in\mathbb F_p^\times} g(d\cdot A)\;\ge\; 2p/|A|-2.
\]
At \(|A|\sim\sqrt p\) this is a gap of \(2\sqrt p-2\). Green records
this as the limit of the polynomial method.

## Tonight

A certified improvement of the universal constant 2, or a documented
residue with replayable compute. Small-prime extremizer tables are
residue unless they imply a larger universal \(C\).

## Outcome

Residue. Shakan’s 2 is still the published leading constant. The
homogeneous Rédei slice used to prove it cannot see \(C>2\). Exact
\(G(p,\mathrm{round}\sqrt p)\) for \(p\le 71\) and the failed lifts
are in `ATTACK.md`, `WALKTHROUGH.md`, `RESEARCH.md`, `compute/`.

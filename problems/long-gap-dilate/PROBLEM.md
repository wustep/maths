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

Let $p$ be prime and $A\subset\mathbb Z/p\mathbb Z$. Write $g(A)$
for the longest run of consecutive residues missed by $A$, and
$d\cdot A=\{da:a\in A\}$. Green #32: if $|A|=\sqrt p$, is there a
dilate with $g(d\cdot A)\ge 100\sqrt p$?

Shakan (2020): for every $A$ with $|A|>1$,
$$
  \sup_{d\in\mathbb F_p^\times} g(d\cdot A)\;\ge\; 2p/|A|-2.
$$
At $|A|\sim\sqrt p$ this is a gap of $2\sqrt p-2$. Green records
this as the limit of the polynomial method.

## Tonight

A certified improvement of the universal constant 2, or a documented
incomplete search with replayable compute. Small-prime extremizer tables are
an incomplete search unless they imply a larger universal $C$.

## Outcome

Incomplete search. Shakan’s 2 is still the published leading constant.
Exact $G(p,\mathrm{round}\sqrt p)$ still ends at $p=71$. The search in
`compute/q1/` saturates the rising-factorial Alon degrees, gives a
SAT upper bounds $G(73,9)\le 24$, $G(79,9)\le 26$,
$G(83,9)\le 27$, $G(89,9)\le 30$ without certified floors (Cadical
gives $G(73,9)\ge 23$), and finds no $C\to 2$ family through
$p=199$. Residue, not a dent.

# The 1/3–2/3 conjecture for posets

- Slug: `one-third-two-thirds`
- List: P34
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Order theory / combinatorics
- Sources: Chan–Pak linear-extensions survey; Open Conjecture Formalizations
- Started: 2026-08-17

## Statement

Every finite non-chain poset is conjectured to contain incomparable (x,y) for which the probability that x<y in a random linear extension lies in [1/3,2/3]. The general case is still open beyond many special classes.

## Tonight

A certified census of a new finite order, a new structural class with a replayable proof, or an exact minimal counterexample candidate with independently checked linear-extension probabilities. Fetch the current published status before searching.

## Result (2026-08-17)

Width-3 \(\delta\) through 9 elements independently recovered as \(\ge 14/39\). At 10 elements there is a unique unlabelled width-3 poset \(W_{10}\) with \(\delta=6/17<14/39\), \(e=187\). Replay `compute/verify_W10.py`. The unrestricted conjecture is still open. See ATTACK.md / WALKTHROUGH.md.

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

Width-3 $\delta$ through 9 elements independently recovered as $\ge 14/39$. At 10 elements there is a unique unlabelled width-3 poset $W_{10}$ with $\delta=6/17<14/39$, $e=187$. Replay `compute/verify_W10.py`. The unrestricted conjecture is still open. See ATTACK.md / WALKTHROUGH.md.

## Result (2026-08-27)

Gupta arXiv:2607.23926v2 is a full order-14 $\delta$-census; the 17 August note had cited v1. Independently: $L_{14,1,9}$ has $\delta=254/725$, and Gupta's width-3 $6/17$ tail row is an ordinal sum. No width-3 poset on $\le 14$ elements has $\delta<6/17$. The broken-rung non-sum minimum is replayed through 14 and computed through 21; at 21 it is $5402/15485\approx 0.348854$. No certified width-3 example below $6/17$. Conjecture still open. Replay `cd compute/q1 && ./run_all.sh`.

## Result (2026-08-27, continued)

The leftover class tables are now complete: ladders through 22, three-rail through 15, naturally labelled interval orders through 10. At 22 the ladder minimum is $1065/3049\approx 0.349295$, above $1/3$. Every three-rail poset through 15 has $\delta\ge 30572/78185>6/17$. Every naturally labelled interval order through 10 has $\delta\ge 1/3$ (counts match OEIS A367494). No $\delta<1/3$. No width-3 example below $6/17$. Conjecture still open. Replay `cd compute/q2 && ./run_all.sh`.

# Push graph reconstruction beyond 13 vertices

- Slug: `graph-reconstruction-next-order`
- List: P39
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Graph theory / computation
- Sources: McKay, Reconstruction of small graphs and digraphs (arXiv:2102.01942); 2026 status summaries
- Started: 2026-08-17

## Statement

The Kelly–Ulam reconstruction conjecture is verified for all graphs through 13 vertices but remains open in general. A fully certified verification at the next order (n=14), or a structural reduction that makes that verification possible, is itself open.

## Tonight

A certified reconstruction result at n=14 (or a clean obstruction / reduction with an independently checkable certificate), or a documented incomplete search. Isolated unlabeled-graph enumerations without a verifier are not a new bound. Fetch McKay's current status before searching.

## Outcome (2026-08-17)

SuperGrok listed 8,571,837 unlabelled n=14 graphs of sequence 4^11 6^3 and claimed unique full decks. Independently counted the g6 list, census-checked every degree sequence as 4^11 6^3, and replayed 17,143 `labelg` deck hashes (0 mismatches). Did not independently re-sort 8.5M hashes. McKay all-graphs n=13 unchanged. See `WALKTHROUGH.md`.

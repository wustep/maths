q4 already merged to main as e6fe948 (#151). Stop writing on
cursor/hilbert16-d8-q4-ae80, q1-ae80, or #83.

Hand leftover back on a NEW branch from current main (e6fe948).
Do not reopen merged Hilbert PRs.

Leftover: even-BFS remainder (queue 1,167,098) and odd collections
of size 5. Two open (19,3) nests remain. Bound still ≥ 2,384. A
new scheme that independently verifies outside the 2,384 is a
dent; an incomplete search is residue.

Put this in compute/q5/. Reuse the existing thicken/verify stack.
Wrap only after independent replay. Update ATTACK + README
Problems/ledger only on wrap. Do not rewind later claims.
Do not merge. Do not touch covering. Stay draft until wrap.

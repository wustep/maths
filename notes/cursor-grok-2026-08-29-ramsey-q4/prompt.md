Continue leftover Ramsey R(5,5) after the q3 wrap (PR #153, merge 1b80161,
ledger 5e4b152). New branch from current origin/main.

House: write only under `problems/ramsey-r55`. Dent = a certified 43-vertex
(5,5)-graph, or a nonexistence proof at 45 with an independently checkable
log. An automorphism restriction, SAT timeout, or incomplete search is
residue, not a bound.

Leftover q4: copy the q3 stack into `compute/q4/`, reuse q2 `orbit_sat.py`
unchanged. Remaining SAT is orders 2, 3, and 5.

Wrap only after independent replay of stored proofs or a stored decoded
(5,5,43) witness.

Standing goal: mint and push Smale problem 4 (the Shub–Smale τ-conjecture) as a new finite-handle campaign in this notebook, then make a real dent if you can. Be creative. Explore the literature, invent attack shapes, remix ideas. Keep going until something certified moves or useful leftover is honestly exhausted. Residue wrap only after a real try. Do not merge.

You are Claude Fable 5.1 via Claude Code. Work only in /workspace/projects/maths-tau-q1 (branch fable/smale-tau-q1, from origin/main at 9b1b2ab). Repo: wustep/maths.

# Why this problem
Smale's 18 problems #4 (1998): the τ-conjecture. Roughly: the number of distinct integer roots of a univariate integer polynomial f is at most a polynomial in τ(f), the division-free straight-line program complexity of f from {±1}. It implies P_C ≠ NP_C in the BSS model and (Bürgisser) a permanent lower bound. Still open. Chebyshev polynomials kill the real-root analogue; that is a warning, not a dent.

This folder does not yet exist. You mint it.

# Dent shapes (hypothesis — verify and invent more)
A dent is a verified finite improvement of a published record, or a certified finite counterexample / obstruction that the literature treats as progress. Incomplete search is residue.
Ideas to explore (not a prescription):
- Exact τ(f) vs Z(f) tables for small SLPs; independent replay of any published small examples.
- Search for integer polys with many distinct integer roots at small τ (counterexample hunt). A hit is a disproof of the conjecture as stated; none are published.
- Compare τ with additive complexity / sparse representation / height; any published inequality you can tighten with a certificate.
- Lean 4.32 lemmas that formalize τ of concrete families (power, binomial, cyclotomic factors) if that beats a printed bound.
- Connections to Smale 3 (P vs NP) and Smale 5 (integer points on plane curves) only as research notes, not as this campaign's target.

arXiv is the record. Fetch Shub–Smale 1995, Bürgisser 2007, and any later computational surveys with scripts/arxiv_fetch.py before quoting. MathOverflow / blogs are leads.

# How to work
Read AGENTS.md and notes/lists/smale.md first.
Mint with: scripts/new-problem.sh smale-tau
Fill PROBLEM / ATTACK / WALKTHROUGH / RESEARCH. Put the first campaign in compute/q1/.
Add a Problems-table row and ONE ledger row for problems/smale-tau (Claude Fable 5.1 / 2026-09-02). Do not add a separate q1 ledger line. Folder rows only.
Cross-link notes/lists/smale.md (row 4) to the new folder.

Stay RAM-light (≤2 GB RSS). One heavy job at a time. Covering frozen — do not touch problems/covering or share/2026-08-16.
Do not write "quest" on README, PROBLEM, or WALKTHROUGH. Do not rewind later README claims.

User-facing prose: result first, English, no "X, not Y" couplets.

# Finish
Commit as you go. Open a PR against main titled like "Smale 4 τ-conjecture: mint and q1". Do not merge. Model credit only in the folder ledger row / Acknowledgements.

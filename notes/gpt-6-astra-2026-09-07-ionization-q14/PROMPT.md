# Campaign prompt

User instruction, received 2026-09-06:

> Dent hunt on Simon 2000 #9 (ionization excess) in this repo checkout.
>
> Goal: certified novel finite improvement of the leading coefficient below the notebook record 1.1006 (same HPS-style chain: N_c < c Z + O(Z^{1/3}) for Z≥4), or another replayable finite bound improvement. Incomplete search = residue, not a lower bound.
>
> Read first: AGENTS.md, problems/simon-ionization-excess/PROBLEM.md, ATTACK.md, WALKTHROUGH.md, RESEARCH.md, compute/record.json, and the latest compute/q* notes. Create compute/LEAVES.md from finite handles if missing. One leaf per quest. This campaign is compute/q14/ with CLAIM.md stating the exact inequality, prior record, and falsifier. run_all.sh exit 0 must mean the CLAIM holds.
>
> Constraints:
> - Covering is frozen; do not touch problems/covering or share/.
> - Do not rewind README Problems-table claims.
> - RAM-light; one heavy job at a time (box is ~16GB).
> - Ledger: one folder row; model name GPT-6 Astra + date only — never write 20xx or wustep in README.
> - Independently verify every claimed number (second implementation / replay).
> - Commit often on branch codex/ionization-q14. When dent certified or leftover exhausted / tokens low: wrap, open an unmerged PR, stop.
>
> Start by writing LEAVES + q14/CLAIM for the chosen leaf, then attack.

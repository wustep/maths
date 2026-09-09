---
name: hunt
description: Run a finite-handle dent hunt on a wustep/maths problem leaf. Use when starting or continuing a campaign, wrapping residue, or filing a steal.
---

# Hunt

Follow [`notes/process/LOOP.md`](../../../notes/process/LOOP.md). Nouns in [`AGENTS.md`](../../../AGENTS.md).

## Steps

1. Read `PROBLEM.md`, published record (arXiv fetch), and `compute/LEAVES.md`. Mint LEAVES if missing.
2. Claim one **open** leaf and one polarity (construction / barrier / alternate-model).
3. Work in `compute/qN/` with `CLAIM.md`. One heavy job at a time. Covering frozen unless Stephen says otherwise.
4. Dual-check any asserted number. Rejection controls on witnesses. `run_all.sh` exit 0 before claiming a dent.
5. Update LEAVES (`certified` = dent, `residue` = incomplete). Append one steal paragraph to `notes/process/STEALS.md`.
6. Commit. Open an unmerged PR. Do not merge. Ledger: one folder row, model name + date only (never plan names).

## Do not

- Treat SAT UNKNOWN / timeout as a lower bound.
- Write “quest” on README, PROBLEM, or WALKTHROUGH.
- Invent status nouns beyond dent and residue.
- Start a second heavy job on a crowded machine.

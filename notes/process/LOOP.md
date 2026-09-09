# Hunt loop

One loop for every finite-handle campaign:

1. **Pick a leaf** from `compute/LEAVES.md` (or mint LEAVES from PROBLEM’s finite handles).
2. **Pick a polarity** on that leaf: construction (explicit witness), barrier (exclusion / method ceiling), or alternate-model (different engine / encoding).
3. **Attack** in `compute/qN/` with one heavy job at a time.
4. **Dual-check** any asserted number (two independent paths; rejection controls on witnesses).
5. **Outcome**: dent (verified improvement of a published record) or residue (incomplete search — never a lower bound). Update `CLAIM.md` and LEAVES.
6. **Steal**: one paragraph into [`STEALS.md`](STEALS.md) when a route dies or a dent certifies. Then stop or pick the next leaf.

## Before claiming a dent

1. Prior art opened (arXiv fetch / replay).
2. `CLAIM.md` exact (inequality or predicate, prior record, falsifier).
3. Two independent checks; `run_all.sh` exit 0.
4. Rejection controls on the witness (known-good accepts, known-bad rejects, empty fails).
5. LEAVES updated.

## Pointers

- Runbook nouns and folder layout: [`AGENTS.md`](../../AGENTS.md)
- Optional progress-shape tags: [`SHAPES.md`](SHAPES.md)
- Agent recipe: [`.claude/skills/hunt/SKILL.md`](../../.claude/skills/hunt/SKILL.md)

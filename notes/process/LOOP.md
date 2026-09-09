# Hunt loop

One loop for every finite-handle campaign. Nouns and folder layout:
[`AGENTS.md`](../../AGENTS.md).

1. **Pick a leaf** from `compute/LEAVES.md`. If LEAVES is missing, mint it from the finite handles in `PROBLEM.md`. Prefer an `open` leaf. One leaf per campaign.
2. **Pick a polarity**: construction (explicit witness), barrier (exclusion or method ceiling), or alternate-model (different engine or encoding). Polarity is how you attack, not a status.
3. **Attack** in `compute/q<n>/` with a `CLAIM.md`. One heavy job at a time.
4. **Dual-check** any asserted number: two independent paths, and rejection controls on the witness (known-good accepts, known-bad rejects, empty input fails).
5. **Outcome**: dent (verified improvement of a published record; write the inequality) or residue (incomplete search; never a lower bound). Update CLAIM and LEAVES.
6. **Steal**: append one paragraph to [`STEALS.md`](STEALS.md) when a route dies or a dent certifies. Then stop or pick the next leaf.

## Before claiming a dent

- Prior art opened (arXiv fetch and replay), cited in `RESEARCH.md`.
- `CLAIM.md` exact: inequality or predicate, prior record, what would falsify it.
- Two independent checks. `run_all.sh` exit 0.
- Rejection controls run.
- LEAVES row set to `certified`.

A dead route still leaves a residual leaf in LEAVES. A method ceiling
(“technique T cannot beat X”) is progress even when the published bound
sits still. An anneal, PINN, or SAT UNKNOWN dump is measurement, not
proof, until a verifier closes it.

# Attack log — S(7) lower bound

## 2026-08-16 — q1

- Searched for a 7-coloring of [1697]. No coloring found. Near-coloring with 2 violations recorded (the recovered `near_1697_two_violations.txt` is empty — the actual coloring bytes were not in the Add-File patch).
- Scripts recovered: `search_shifted_sat.py`, `search_almost_symmetric_pysat.py`, `search_orbit_minconflicts.py`, `search_seed_multipliers.py`, `repair_near_coloring.py`, `verify_coloring.py`.
- Lean stub: `lean/Schur1697SymmetryObstruction.lean`.
- Memory: commit `61e0369` — S(7) no 1697 coloring.

## 2026-08-16 — q2

- m=144 seed; still 2 violations. Scripts: `q2_alternate_template_search.py`, `q2_exact_sat.py`, `q2_seed_cegar.py`, `audit_q2_residue.py`.
- RESEARCH.md recovered: Rowley ancillary XLS could not be ingested; no 1696 specimen copied.

## 2026-08-23 — q3 shapes before search

The target object is always an explicit list of 1,697 colors in `0..6`
accepted by `compute/verify_coloring.py --expect-length 1697`. Such a list
would prove the dent $S(7)\geq1697$. An obstruction certificate only rules
out its named ansatz; it is not an upper bound for $S(7)$.

Ranked by the cost of the first decisive check, with the chance of a real
bound used to break ties:

1. **Recover or reconstruct the q1 two-violation coloring, then repair it.**
   The replayable finish is the recovered 1,697-vector, its two exact bad
   triples, a bounded repair script, and a verified repaired vector. First
   search git objects and surviving logs for the missing bytes; if that
   fails, reconstruct the precise almost-reflection family and ask only for
   a two-defect specimen before running a local ejection-chain/MaxSAT repair.
   Do not rerun q1's unrestricted SAT, generic orbit min-conflicts, seed
   multiplier sweep, or the same guessed q2 split sets.
2. **Extend Rowley's published 1,696 coloring by a sparse ejection chain.**
   This shape was not available in the folder before q3. Its certificate is
   Rowley's extracted base vector, a short edit list including 1697, the
   resulting exact vector, and the independent verifier report. The cheapest
   check is to verify the workbook vector, append each of seven colors, and
   enumerate the resulting boundary conflicts; bounded-Hamming SAT then tests
   whether a small edit set can clear them. Do not replace the base by the
   Fredricksen--Sweet seed or search all colorings from scratch.
3. **Use a different symmetry: reflection about 1698 with a sparse, chosen
   exception set.** A model expands to a 1,697-vector and therefore gives the
   required dent. The first check computes which reflection pairs of the
   verified Rowley coloring already disagree and ranks additional splits by
   the conflicts they unlock; SAT is run only after this structural scan.
   Do not impose q1's fully symmetric ansatz or repeat q2's split pairs chosen
   from the lost near-coloring.
4. **Lift a base coloring with a shifted/template construction.** The finish
   is a finite Bengone-style template table, a generator from a verified base
   coloring, and the generated 1,697-vector plus verifier. The cheap check is
   the size/color arithmetic followed by the finite template admissibility
   test. The published width-10 shifted template gives
   $10S(5)+2=1602$, so it does not itself reach 1697; only a genuinely new
   seven-color parameter set survives. Do not rerun the old script merely
   called `search_shifted_sat.py`, which encodes reflection rather than
   Bengone's shifted-label definition.
5. **Prove a finite obstruction under a named symmetry.** For full reflection
   $c(x)=c(1698-x)$, a satisfying model would expand to the desired coloring;
   an UNSAT certificate only excludes that family. The one-page check kills
   it immediately: reflection equates 566 and 1132, while
   $566+566=1132$. The existing Lean lemma is the intended replay artifact
   once its source encoding and build are audited. Do not send this ansatz to
   SAT again.
6. **Build from a smaller Schur coloring by an exact product/blowup.** The
   certificate would be the smaller coloring, finite template, deterministic
   generator, and verified 1,697-vector. Size arithmetic kills the standard
   available choices: Schur from $S(6)\geq536$ gives 1609, Abbott--Hanson from
   $S(5)=160$ gives 1444, Bengone's shifted template gives 1602, and Rowley's
   five-color template applied to $S(2)=4$ gives 1664. None reaches 1697, so
   this shape is dropped unless a new template with an explicit finite
   certificate is found. No generic product search will be run.
7. **Search a cyclic modular coloring, a shape not present in q1/q2.** The
   certificate is a seven-coloring of the nonzero residues modulo 1698 with
   no monochromatic modular equation, plus a modular verifier; restricting it
   to representatives 1 through 1697 would be the desired interval coloring.
   The first check is a small modular encoding calibration and its forced
   orbit/unit constraints. This stronger object is lower-ranked because it may
   fail even when an interval coloring exists. Do not treat modular UNSAT or a
   timeout as evidence about unrestricted $S(7)$.

Shapes 1--4 and 7 survive as construction routes. Shape 5 is already a named
symmetry wall, and shape 6 is already an arithmetic wall for the published
off-the-shelf constructions.

## 2026-08-23 — q3 source recovery and first checks

- The q1 two-violation bytes are not recoverable from this repository. The
  tracked file and the sole unreachable commit containing the old Schur
  campaign both point to the empty blob. No unreachable blob is a 1,697-token
  vector over `0..6`. Shape 1 therefore survives only as reconstruction, not
  recovery.
- Rowley's ancillary workbook was recovered from the official arXiv source
  archive. `compute/q3/rowley_1696.txt` is its exact zero-based color column
  (SHA-256 `feef1da7...c40896`). The independent verifier accepts all 719,104
  pairs, with class sizes `204,176,318,152,148,200,498`.
- The specimen has no mismatches under reflection about 1697. Giving 1697
  colors 0 through 6 creates respectively `102,88,159,76,74,100,249`
  boundary conflicts. For each color these are vertex-disjoint complement
  pairs, so a repair that keeps the appended color must recolor at least that
  many old entries. This kills a direct or very-small-edit lift of this
  specimen, but not a larger ejection chain or an unrestricted coloring.
- The full-reflection obstruction source had mojibake in place of Lean
  symbols. It was rewritten with ASCII syntax and now compiles under the
  pinned Lean 4.32.0 using `lean lean/Schur1697SymmetryObstruction.lean`.

---
name: new-problem
description: Mint a new problems/<slug>/ folder with the standard files and README rows. Use when starting an attack on a problem that has no folder yet.
---

# New problem

1. Pick a kebab-case slug and create `problems/<slug>/` with:

   ```
   PROBLEM.md        statement and what would count as a dent
   ATTACK.md         chronological attempts
   WALKTHROUGH.md    discovery notes, not a cleaned proof
   RESEARCH.md       papers, OEIS, failed lookups
   compute/          verifier plus certificate
   lean/             only if there is a lemma
   ```

2. `PROBLEM.md` header: slug, list ref, solver, status, area,
   sources, started date — then the statement and an explicit
   dent criterion, including what does not count (see
   `problems/chowla-cosine/PROBLEM.md`).
3. `ATTACK.md` is dated and chronological; append, never
   reorder. False starts stay in.
4. `WALKTHROUGH.md` follows the beats in
   `refs/walkthrough-style.md`. Empty sections are fine until the
   quest is done; do not clean the path.
5. `RESEARCH.md` lists only URLs actually opened (see the
   literature skill).
6. `compute/` needs a replay entry point (`run_all.sh` or a
   single verify script) alongside the certificate.
7. Lean lemmas live in the problem folder; `lean-toolchain` pins
   4.32.0.
8. Add a README Problems-table row (folder link, honest status).
   Add a "Which model ran what" ledger row when you actually run.

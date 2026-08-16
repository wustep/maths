You are working in the maths repo at /workspace/maths (github.com/wustep/maths), already checked out. Do not clone. Work on a new branch `covering-result` off current main. Commit when the pipeline is green. Open a PR with `gh pr create` if the GitHub remote works. Do not merge. Do not force-push.

Git author if you commit (env only, never `git config`):
  GIT_AUTHOR_NAME='Stephen Wu'
  GIT_AUTHOR_EMAIL='wustep@users.noreply.github.com'
  GIT_COMMITTER_NAME='Stephen Wu'
  GIT_COMMITTER_EMAIL='wustep@users.noreply.github.com'

# QUARANTINE — read this first

`problems/covering/_reference/` is a scaffold kit from a prior Claude session.

- `problems/covering/_reference/data/` is SAFE to read anytime (matrices, partition JSON).
- `problems/covering/_reference/scripts/` is QUARANTINED. Do NOT read, open, cat, or import anything under `_reference/scripts/` until BOTH of your verifiers in `problems/covering/result/verify/` are written AND `run_all.sh` is passing. Then you may diff your numbers against the oracle.
- Do not copy oracle code. Two implementations that share an encoding convention are one implementation.
- Do not modify `problems/covering/compute/`. Copy what you need.
- After you finish, either delete `_reference/` before the final commit, or keep it and say plainly in NOTE.md that it was the scaffold. Prefer keeping `_reference/README.md` + data and deleting `_reference/scripts/` from the commit if you used the oracle only as a post-hoc diff.

# Job

Build `problems/covering/result/` as a self-contained, independently reproducible, submission-grade artifact for the full covering-code result, including the QM₂² propagation the original overnight run missed.

The overnight agent produced a binary [50,40]₂ code of covering radius 2, certifying ℓ₂(10,2) ≤ 50. That result is real and independently re-verified, but the folder undersells it and disclaims the consequence that actually matters: the r=10 seed re-seeds Davydov–Marcugini–Pambianco's entire R=2 iterative family.

# Background you must internalize before writing any code

Notation: ℓ₂(r,R) is the smallest length of a binary linear code with codimension r and covering radius R. For an r × n parity-check matrix H with column set S ⊂ F₂^r, covering radius ≤ 2 is equivalent to {0} ∪ S ∪ (S+S) = F₂^r.

The reference is Davydov, Marcugini, Pambianco, "New upper bounds for binary linear covering codes", arXiv:2511.02542 (Nov 2025). Fetch it. Read at minimum: Definition 3.2 (the (R,ℓ)-partition), Theorem 4.1 (Constructions QM₁²/QM₂²), Theorem 4.3 (the Kaikkonen–Rosendahl [51,41]₂2 code), Theorem 5.2 (their computer-searched 2-partition with p(H_KR) = 11), and Theorem 5.7 with its proof (the iterative family).

The load-bearing fact: their entire R=2 infinite family is seeded by the r=10 entry. Table 5.1 row r=10 reads n = 51, reference [50] = Kaikkonen–Rosendahl 2003, density 1.29590 — and it is not bolded, meaning even this Nov 2025 paper did not improve it. It has stood since 2003. Theorem 5.7(i) says outright that the 2-partitions of H_KR are "very important for the next iterative process."

So a 50-column matrix at r=10 does not merely shave one column off one table cell. If it admits a small enough 2-partition, it re-seeds the whole family.

Note: `problems/covering/PROBLEM.md` currently quotes Green's Problem 40 range as 1 ≤ f(2) ≤ 1.4238. That is stale — arXiv:2511.02542 already improved the upper bound to ≈1.3203. Fix this in the new note; do not propagate the error.

# Start order

1. Fetch arXiv:2511.02542 (PDF + HTML/abs). Read the sections listed above.
2. Write `problems/covering/result/VERIFY_PLAN.md` — your plan for the two independent verifiers — BEFORE writing verify code.
3. Then implement.

# Verified inputs (treat as claims; verify with your own code)

The 50 columns of H, as integers over F₂^10 (bit i = row i+1, LSB first). These match `problems/covering/compute/witness_r10_n50.json`:

1 2 4 15 16 32 65 86 128 173 183 202 212 247 256 297 320 329 341 366 373 381 391 403 438 460 479 491 502 559 576 608 653 734 742 754 771 777 789 821 846 855 869 881 893 897 927 981 1003 1004

A valid (2,0)-partition into 10 blocks (the new ingredient the original run never computed):

- block 0: [2, 128, 202, 212, 771, 855, 897, 981]
- block 1: [86]
- block 2: [381, 893, 1003]
- block 3: [183, 297]
- block 4: [1, 65, 247, 256, 320, 438, 502, 734]
- block 5: [15, 173, 329, 366, 460, 559, 653, 846]
- block 6: [4, 16, 391, 491, 742, 754, 869, 881]
- block 7: [479, 1004]
- block 8: [403]
- block 9: [32, 341, 373, 576, 608, 777, 789, 821, 927]

This gives p(H) = 10, versus the paper's p(H_KR) = 11. If any check fails, STOP and report — do not patch around it.

Safe copies of generated matrices also live in `_reference/data/` (H_r18_n815.txt, H_r20_n1631.txt, kr_r10_n51.txt, partition_p10.json). You may read those as comparison witnesses. Your `build_propagation.py` must construct r=18 and r=20 itself. If your independent construction produces different matrices that both verify, that is a stronger result (two distinct witnesses). If they differ and only one verifies, stop and report immediately.

# Encoding warning (easy to get wrong)

The KR hex in the paper (Theorem 4.3) is MSB-first with row 1 as MSB. Everything else in this repo is LSB-first (bit i = row i+1). A from-scratch verifier that misses the reversal will produce a spurious mismatch on the KR baseline. Document the convention in NOTE.md and in the verifier comments.

# What to build

```
problems/covering/result/
  NOTE.md
  RESULT.md
  PRIORITY.md
  note.tex
  VERIFY_PLAN.md
  data/
    H_r10_n50.txt         copied from ../compute/, unchanged
    partition_p10.json    columns + block assignment, with a schema comment
    H_r18_n815.txt        generated by your builder
    H_r20_n1631.txt       generated by your builder
    kr_r10_n51.txt        KR baseline, reconstructed from hex
  verify/
    verify.py             verifier #1 — written from scratch
    verify.rs or verify.c verifier #2 — INDEPENDENT reimplementation
    build_propagation.py  constructs the r=18 and r=20 matrices
  run_all.sh
  Makefile                optional
```

# Verifier requirements

Write two verifiers in two different languages, and write the second one without looking at the first. Each must independently:

1. Parse the matrix from its text file (not from JSON).
2. Confirm all columns are distinct, nonzero, and of the right width.
3. Compute F₂-rank and confirm it equals r.
4. Exhaustively enumerate {0} ∪ S ∪ (S+S) and confirm it equals all of F₂^r. Enumerate honestly — no early exit, no trusting a stored certificate.
5. Confirm covering radius is exactly 2 (some syndrome is neither 0 nor a single column).
6. Report the multiplicity histogram and the covering density as an exact rational.
7. Separate partition checker: for every syndrome s that is neither 0 nor a column of H, confirm there exists a pair hᵢ + hⱼ = s with i, j in distinct blocks. Syndromes equal to 0 or to a single column are satisfied by definition.

# Propagation

Implement Construction QM₂² (Theorem 4.1, eq. 4.2 and 4.4) directly from the paper. Do not hand-wave it.

Starting code: n₀ = 50, r₀ = 10, p(H₀) = 10.

Condition to check explicitly in code: n₀ ≥ 2^m ≥ p(H₀). This permits m = 4, 5 and not m ≥ 6 (since 2^6 = 64 > 50). Assert this rather than assuming it.

Indicators: assign βⱼ ∈ F_{2^m} such that columns in distinct blocks get distinct indicators, and the union of indicators used covers all of F_{2^m}. Since indicator sets must be disjoint across blocks, this needs Σ_b |I_b| = 2^m with |I_b| ≤ |block b| — write a greedy allocator and assert feasibility. Block sizes here are [1,1,2,2,3,8,8,8,8,9], summing to 50.

Columns of A(hⱼ, βⱼ): (hⱼ, ξ, βⱼ·ξ) for all ξ ∈ F_{2^m} including ξ=0.

D = D₁(2): the 2^m − 1 columns (0_{r₀}, 0_m, w) for w ranging over the nonzero m-bit vectors (parity-check matrix of the Hamming code).

Field arithmetic: GF(16) with x⁴+x+1 (0x13), GF(32) with x⁵+x²+1 (0x25). Include a small self-test that multiplication is associative and that every nonzero element has an inverse.

Then run the full exhaustive covering check on each result. Do not sample.

# Hard assertions

`run_all.sh` must assert every one of these and fail loudly otherwise:

- r=10 matrix shape 10 × 50, rank 10, 50 distinct nonzero columns
- r=10 coverage 1024 / 1024
- r=10 density exactly 319/256 = 1.24609375
- r=10 representation multiplicity histogram {1:859, 2:129, 4:24, 5:9, 6:3}
- syndromes needing a pair 973
- pair-only multiplicity histogram over those 973 {1:821, 2:123, 4:19, 5:8, 6:2}
- forced-split pairs (unique representation) 821
- partition validity: valid (2,0)-partition, 10 blocks
- KR baseline: 51 distinct columns, 1024/1024, density 1327/1024
- r=18 propagation (m=4): n = 815, 262144 / 262144, density 332521/262144 ≈ 1.26847
- r=20 propagation (m=5): n = 1631, 1048576 / 1048576, density 1330897/1048576 ≈ 1.26925
- MINIMALITY (new): deleting any one of the 50 columns leaves at least 9 uncovered syndromes. This is an LO code / minimal 1-saturating 50-set in PG(9,2).
- DEPENDENT TRIPLES (new): minimum distance 3; exactly 10 linearly dependent triples; the triple (491, 734, 821) sits in three distinct blocks (blocks 6, 4, 9). Analogue of the paper's Theorem 5.2(ii), needed for the QM₅² step at r=28.

If a number in this prompt disagrees with what your code computes, the code wins — stop and tell me in RESULT.md. Never fabricate. If a paper fetch fails, write UNVERIFIED.

# The family

From the recurrence n_new + 1 = 2^m (n₀ + 1), r_new = r₀ + 2m, derive and state the closed form n = 51·2^{r/2−5} − 1 for the reachable even r, with asymptotic covering density → 51²/2^{11} = 2601/2048 ≈ 1.26999.

Compare against: the paper's new μ̄(2) ≈ 1.32031 and the prior μ̄(2) ≈ 1.4238 that had stood since 1992. Since Green's f(2) is a liminf over r, and the even-r subsequence attains this density, note that this also bounds f(2) ≤ 2601/2048.

Be careful and explicit about which even r are reachable by iterating QM₂² from this seed (each step requires n₀ ≥ 2^m ≥ p(H₀), and QM₂² gives p(H_C) ≤ 2^{m+1} + 1). Produce a generated table of reachable r up to 64 with n, density, and the corresponding published value, and mark which rows are improvements. Generate this table with code, not by hand.

Soft spot (flag in NOTE.md): m=4 and m=5 from the base seed are exhaustively verified. Steps beyond that inherit the paper's p(H_C) ≤ 2^{m+1}+1 bound rather than computing partitions directly. That is the claim a referee will push on first. If budget allows, compute those partitions explicitly.

# NOTE.md

Aim for something a coding-theory referee could act on in ten minutes:

1. Statement. ℓ₂(10,2) ≤ 50, with the matrix inline.
2. Why it matters. The r=10 seed argument. This is the section the original walkthrough is missing entirely.
3. The 2-partition. p(H) = 10 ≤ p(H_KR) = 11.
4. Minimality. LO code / minimal 1-saturating set in PG(9,2); best single deletion leaves 9 uncovered syndromes.
5. Dependent triple. (491, 734, 821) across blocks 6/4/9; analogue of Thm 5.2(ii); r=28 branch.
6. Propagation. QM₂² at m=4, 5, exhaustively verified, then the family and asymptotic density.
7. Verification. How to re-run; both verifiers ignore any stored certificate and enumerate from the matrix text.
8. What is not claimed (be aggressive):
   - 50 is not shown optimal. Sphere-covering only gives ℓ₂(10,2) ≥ 45.
   - The n=49 run leaving 7 uncovered syndromes is search residue, not a lower bound. Say this in those words.
   - The (8,25) and (9,38) gaps remain open.
   - The f(2) bound is an upper bound only; whether f(2) = 1 is untouched.
9. Provenance. The matrix was found by targeted simulated annealing driven by an LLM agent (Codex gpt-5.6-sol, overnight 2026-08-16), seeded from the KR matrix; the partition and propagation were derived subsequently; every claim is exhaustively machine-checkable from the committed matrices. Do not bury this and do not apologize for it.

Every number in NOTE.md must be emitted by code in verify/, not typed by you.

Also draft `note.tex` (article class, ~3 pages, no fancy packages) suitable for arXiv math.CO / cs.IT, with the matrix as an appendix listing.

# PRIORITY.md

A checklist, not prose:

- [ ] Check Lobstein's online covering-radius bibliography for any ℓ₂(10,2) ≤ 50.
- [ ] Search ACCT proceedings (Davydov–Drozhzhina-Labinskaya lineage) — poorly indexed, most likely place a 50 could already be hiding.
- [ ] Check Cohen–Honkala–Litsyn–Lobstein Covering Codes (1997) length tables.
- [ ] Check for any known lower bound on ℓ₂(10,2) better than the sphere-covering bound of 45.
- [ ] Email Davydov ([redacted]) and Marcugini/Pambianco (unipg.it) with the matrix and verifier before posting anything. Draft that email into PRIORITY.md as a fenced block.

Table 5.1 is explicitly "best as far as the authors know" — treat priority as unresolved until a human confirms it.

# Housekeeping

- Update `problems/covering/ATTACK.md` with a dated 2026-08-16 afternoon entry pointing at `result/`.
- Update the repo `README.md` covering row to reflect the propagation. Keep the existing house style.
- Do not delete the honest negative results (n=49 residue, (8,25) and (9,38) failures). They belong in the note.
- Deterministic. No RNG in the committed pipeline. `run_all.sh` must produce byte-identical output across runs.
- No overclaiming. Upper bounds only.
- After both verifiers pass, you may read `_reference/scripts/oracle_check.py` and diff. Do not copy it.

# Done when

`problems/covering/result/run_all.sh` exits 0, both verifiers agree, NOTE.md / RESULT.md / PRIORITY.md / note.tex exist, ATTACK.md and README.md are updated, and the work is committed on `covering-result` with a PR if possible.

Report back: PR URL if any, which assertions passed, any number in this prompt that disagreed with code, and whether your r=18/r=20 matrices matched the reference kit or were distinct verifying witnesses.

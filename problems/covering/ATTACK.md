# Attack log — Linear covering codes of radius two

## 2026-08-16 — q1 (recovered from Codex session 01a009f7-5a24-71e1-bf4c-9667f4d2cbc4)

- Targets tried: \((r,n)=(8,25)\) (documented 26) — best anneal missed 3 of 256 syndromes; CP-SAT/Z3 no model. \((9,38)\) (documented 39) — CP-SAT UNKNOWN; Gabidulin 39-set deletions missed 8.
- Click: seed from the 51-column Kaikkonen–Rosendahl matrix at \(r=10\). Fixed-cardinality targeted simulated annealing, xorshift64 run 0, hit 0 uncovered at proposal 3,600,281.
- Witness: 50 distinct nonzero 10-bit columns. F\(_2\)-rank 10. Exhaustive pair-XOR: 1024/1024. Density \(319/256=1.24609375\).
- Commit remembered in Math-agent memory as `5b93f34`. Watcher (Grok, 03:32 PT) independently rebuilt columns from `H_r10_n50.txt` (LSB = row 1) and confirmed 1024/1024.
- \(n=49\) stochastic run left 7 uncovered syndromes — not a lower bound.

## 2026-08-16 — q2 (recovered from Codex session 01a00a33-832e-7d13-bf0e-59aeab97ec82)

- Push 50→49 using `H_r10_n50.txt` as seed. Search residue still 7 uncovered. Files: `search_n49.c`, `search_n49_lifted.c`, `build_q2_residue.py`, `verify_q2_residue.py`.
- Do not claim \(f(2)\). Holes \((8,25)\) and \((9,38)\) remain secondary.

## 2026-08-16 afternoon — q3 (Claude, `covering-result` branch)

- Built [`result/`](result/) as a self-contained, independently reproducible artifact for the whole result. Run it with `cd problems/covering/result && ./run_all.sh` — 74 checks, exit 0, byte-identical output across runs.
- Two verifiers from scratch, two languages, opposite algorithms: `result/verify/verify.py` is pair-driven, `result/verify/verify.rs` is syndrome-driven. `run_all.sh` diffs their fact dumps. Both re-derive everything from the matrix text; neither reads a stored certificate. A third, quarantined oracle was run only afterwards and agreed on every value; it is not in the tree.
- The missing piece the overnight run never computed: a valid \((2,0)\)-partition of \(H\) into **10** blocks, against the paper's computer-searched \(p(H_{KR})=11\) (arXiv:2511.02542 Thm 5.2). All 973 syndromes that need a pair have a cross-block one; 821 of them have a unique pair, so the partition is tightly forced.
- Minimality: deleting any single column leaves \(\ge 9\) uncovered syndromes (best deletions 381, 479, 927 leave exactly 9). So the 50-set is a minimal 1-saturating set in \(PG(9,2)\) — an LO code. Not padded.
- \(d=3\), exactly 10 dependent triples; exactly one, \((491,734,821)\), spans three distinct blocks (6/4/9). Analogue of Thm 5.2(ii), which is what QM\(_5^2\) needs at \(r=28\).
- Propagation: Construction QM\(_2^2\) (Thm 4.1, eq. (4.2), (4.4)) implemented from the paper. \(n_0\ge 2^m\ge p(H_0)\) permits exactly \(m=4,5\), asserted not assumed. Results exhaustively verified: \(r=18\), \(n=815\), 262144/262144; \(r=20\), \(n=1631\), 1048576/1048576. Published values 831 and 1663.
- These matrices differ from the alternate allocations in [`result/data/alt/`](result/data/alt/) (the indicator allocation is a free choice) and both verify — two distinct witnesses at each \(r\), not one.
- Family: \(n=51\cdot 2^{r/2-5}-1\), \(\bar\mu(2)\le 2601/2048\approx 1.27002\), against the paper's \(2704/2048\approx 1.32031\) and the pre-2025 \(729/512\approx 1.42383\). Even \(r\le 64\) reachable by QM\(_2^2\) from this seed: 10, 18, 20, 30–40, 46–64. Not reachable: 12, 14, 16, 22, 24, 26, 28, 42, 44 — the QM\(_3^2\)/QM\(_5^2\) analogues are not implemented and nothing is claimed there.
- Soft spot, stated in the note: only \(m=4,5\) are exhaustively verified. The rest of the family inherits the paper's \(p(H_C)\le 2^{m+1}+1\) instead of computing partitions. That is the first thing a referee will push on.
- One number in the brief lost to the code: \(2601/2048\) is \(1.27002\), not \(1.26999\). Fraction right, decimal wrong; no bound changes.
- Priority unresolved — Table 5.1 is "best as far as the authors know". Checklist and a drafted email to Davydov/Marcugini/Pambianco in [`result/PRIORITY.md`](result/PRIORITY.md). Nothing goes out before a human works that list.

## 2026-08-18 — q4 (Claude, `cursor/covering-n49-attack-48dc` branch): push 50 → 49

Target: \(\ell_2(10,2)\le 49\) — 49 distinct nonzero 10-bit columns, rank 10, singletons + pair-XORs covering all 1024 syndromes. Budget check: \(1+49+\binom{49}{2}=1226\ge 1024\), slack 202, density would be \(1226/1024\approx 1.19727\). Everything new lives in [`compute/q4/`](compute/q4/); the certified n=50 matrix and `result/` are untouched.

### Angle 1 — symmetry: 49 = 7×7 (new this quest)

If a 49-covering is invariant under a subgroup \(G\le GL(10,2)\), it is a union of \(G\)-orbits, and coverage collapses to orbit-class space (the pair-sum multiset of two orbits is \(G\)-invariant). For \(|G|=7\) the orbit classes number ~147 and a selection is just 7 orbits of size 7 — small enough to exhaust *completely*. Tools:

- [`compute/q4/gen_groups.py`](compute/q4/gen_groups.py) — deterministic generator of subgroup representatives: every cyclic order-\(L\) class for \(L\in\{3,5,7,9,15,21,35,45,105\}\) as block-diagonal companion matrices (deduped by cyclotomic-coset relabeling under \(M\mapsto M^k\)), plus \(C_7\times C_7\) two-generator groups (orbit sizes 1/7/49). One conjugacy representative suffices: conjugation maps invariant coverings to invariant coverings.
- [`compute/q4/orbit_dfs.c`](compute/q4/orbit_dfs.c) — exhaustive DFS over orbit selections with exact weight 49. Safe prunes only: subset-sum budget DP, an optimistic class-count bound, and suffix reachability masks (a class no remaining single/pair mask can cover kills the branch). Witnesses are re-verified in-process by flat pair enumeration and must still pass the Python verifier.
- Validation: planted-witness tests (direct-sum coverings \(W_1^*\cup W_2^*\) are invariant and found at n=62/78), `--no-prune` node-count comparisons, and [`compute/q4/naive_enum.c`](compute/q4/naive_enum.c), an independent dumb enumerator, agreeing on small cases.

Sweep driver: [`compute/q4/run_all_groups.sh`](compute/q4/run_all_groups.sh) → [`compute/q4/orbit_runs.log`](compute/q4/orbit_runs.log). Results so far (each line is an *exhaustive* claim for that subgroup class):

- order-7, trivial part dim 1, blocks \(c_1^3\): **no invariant 49-covering** (4.36e9 nodes, 44 s).
- order-7, trivial part dim 1, blocks \(c_1^2 c_2\): **no invariant 49-covering** (8.94e9 nodes).
- (sweep continuing: order-7 dim-4/dim-7 fixed spaces, order-9, order-15/21/35/45/105, \(C_7\times C_7\) — updated below as they land.)

### Angle 2 — exhaustive k-swap prover from 7-hole residues

[`compute/q4/kswap.c`](compute/q4/kswap.c): given a 49-column configuration, decide *exactly* whether any swap of ≤ K columns reaches zero holes. Re-add search branches on the first live hole (fresh column = hole, hole^kept, hole^placed), with an explicit defer branch for holes covered by two future columns, resolved in an exact endgame (anchored chain closure + floating-pair components, which are always placeable by translation), plus a top-s coverage-count bound that prunes ~300×. Planted controls: corrupting k columns of the certified 50-set (compiled at `-DN_COLS=50`) is caught at exactly j=k for all k = 1, 2, 3, 4.

Baseline stochastic runs (q2 binaries, fresh deterministic seeds) re-hit the 7-hole floor quickly; two 7-hole configs harvested:

- `best_sa_config.cols`: holes {68, 95, 106, 214, 248, 679, 760}
- `best_lifted_config.cols`: holes {52, 471, 483, 544, 706, 833, 931}

**Results.** `best_sa_config` admits **no swap of ≤ 5 columns** reaching zero holes (exhaustive: C(49,5) = 1,906,884 removal sets, 94.6M re-add nodes). `best_lifted_config` admits no swap of ≤ 4 (j=5 running). These local optima are deep.

**Finding: two inequivalent canonical near-misses.** Both hole sets have rank 5 and exactly one zero-sum quadruple (an affine parallelogram) among the 7 holes; both configs have *identical* GL-invariants (multiplicity histogram, unique-coverage distribution per column, dependent-triple count). Yet [`compute/q4/find_equivalence.py`](compute/q4/find_equivalence.py) — color-guided backtracking over basis images, self-tested on identity and random GL(10,2) transforms — proves there is **no linear map sending one 49-set to the other**. The 7-hole floor is not one canonical configuration; the landscape has at least two distinct deep basins with the same signature.

### Angle 3 — SAT with a frame reduction

[`compute/q4/sat_n49.py`](compute/q4/sat_n49.py): full CNF (pair auxiliaries + coverage clauses + seqcounter cardinality ≤ 49) with the WLOG reduction that a rank-10 covering can be assumed to contain all ten unit vectors (GL(10,2) frame normalization). Cadical, long timeout, background. A long shot; UNSAT would be a theorem but is not expected to terminate.

### Wrap (stopped on request, 06:09 UTC)

**No 49-covering found. No dent. Everything below is certified residue / certified exclusion, all replayable.**

- **Symmetry exhaustions** ([`compute/q4/orbit_runs.log`](compute/q4/orbit_runs.log)): 79 subgroup classes exhausted at n=49, **zero invariant coverings in every one**: all 50 \(C_7\times C_7\) classes (orbit sizes 1/7/49 — the "49 = 7×7" resonance is dead for two-generator symmetry), 12 order-15 classes, 10 order-21 classes, 7 order-105 classes, and the two order-7 classes with 1-dimensional fixed space (4.4e9 and 8.9e9 node exhaustions). 11 of the 79 are instant budget infeasibilities (orbit sizes cannot sum to 49, e.g. pure order-3/5/11 actions). **Not settled**: order-7 with fixed-space dim 4 (two classes) and dim 7, plus two order-15 stragglers — timed out at 300–1800 s, no witness seen; and the order-9/-35/-45/-63/-3/-5 files the sweep never reached. Rerun: `CASE_TIMEOUT=big ./compute/q4/run_all_groups.sh` (skips completed cases).
- **k-swap exhaustion**: `best_sa_config` (7 holes) has **no ≤5-swap** to zero holes — exhaustive over all C(49,j) removals, j ≤ 5 (1.9M removal sets, 94.6M re-add nodes, [`compute/q4/kswap5_sa.log`](compute/q4/kswap5_sa.log)). `best_lifted_config` (7 holes): **no ≤4-swap** (j=5 was mid-run when stopped). Prover validated by 4/4 planted controls.
- **Inequivalence**: the two 7-hole optima are *not* GL(10,2)-equivalent despite identical invariant profiles (see Angle 2). At least two distinct deep basins at 7 holes.
- **SAT**: instance built (1.14M clauses), no verdict before stop. [`compute/q4/harvest_optima.sh`](compute/q4/harvest_optima.sh) + [`compute/q4/dedupe_optima.py`](compute/q4/dedupe_optima.py) are ready but unrun.
- Best hole count this quest: **7** (matching q2), now with teeth: provably ≥6-swap-deep (SA config) and two inequivalent basins.
- Certified n=50 matrix and `result/` untouched. Replay: `python3 compute/q4/verify_config.py compute/q4/best_sa_config.cols` (prints the 7 holes); `gcc -O3 ... compute/q4/kswap.c && ./compute/q4/kswap --input compute/q4/best_sa_config.cols --prove 5`; `./compute/q4/orbit_dfs --group compute/q4/groups/<case>.grp --n 49`.
## 2026-08-19 — q5 (Codex, QM\(_3^2\)/QM\(_5^2\) propagation)

- The direct and lifted 49-column searchers ran concurrently for 1228.66 seconds each (7 and 8 threads, all documented modes, master seeds `0x49A202608190001` and `0x49B202608190002`). A new guided add-then-delete/breakout search in [`compute/search_n49_guided.c`](compute/search_n49_guided.c) ran 637.74 seconds on 4 threads. All three best checkpoints independently recount to rank 10, 49 distinct nonzero columns, and 1017/1024 covered: **7 uncovered remains a search residue, not a lower bound**. Checkpoints: `compute/q2_direct_20260819_a.json`, `compute/q2_lifted_20260819_a.json`, `compute/q2_guided_20260819_a.json`.
- Construction QM\(_3^2\) (arXiv:2511.02542 Thm. 5.1) was implemented deterministically in [`compute/build_qm3.py`](compute/build_qm3.py). The seed's 10-block partition is rechecked, the field polynomials are checked for irreducibility, and the matrices are independently checked from text by [`compute/verify_radius2_matrix.c`](compute/verify_radius2_matrix.c). Certified new bounds: \(\ell_2(22,2)\le3325\) (paper: 3389), \(\ell_2(24,2)\le6653\) (paper: 6781), and \(\ell_2(26,2)\le13309\) (paper: 13565). Exhaustive coverage was 4194304/4194304, 16777216/16777216, and 67108864/67108864, respectively; all matrices have full rank and distinct nonzero columns.
- For QM\(_5^2\), [`compute/build_qm5.py`](compute/build_qm5.py) refines the seed partition to 16 blocks and isolates the already-certified cross-block triple \((491,734,821)\). Its alternative \(r=18,n=815\) lift has an explicit, exhaustively checked 33-block partition; this is an intermediate tailored to QM\(_5^2\), **not a re-claim of the existing \(r=18\) bound**. The resulting `compute/H_r28_n26111.txt` has rank 28, 26111 distinct nonzero columns, and exhaustive coverage 268435456/268435456. Its explicit 66-block partition also covers 268435456/268435456 syndromes using only cross-block pairs. Thus \(\ell_2(28,2)\le26111\), improving the paper's 26623 by 512.
- The verified \(p(H)\le66\) at \(r=28\) satisfies the QM\(_2^2\) hypothesis \(26111\ge2^m\ge66\) for \(m=7,8\). The theorem therefore gives \(\ell_2(42,2)\le3342335\) and \(\ell_2(44,2)\le6684671\), improving 3407871 and 6815743. These two large continuations are theorem-propagated from the exhaustively checked matrix/partition; no claim is made that their \(2^{42}\) or \(2^{44}\) syndrome spaces were enumerated.
- Reproduction: run `compute/run_qm3_checks.sh` and `compute/run_qm5_checks.sh` from this problem directory. The builders also reproduced every matrix and partition byte-for-byte in a fresh directory. No optimality or \(f(2)\) claim is made.

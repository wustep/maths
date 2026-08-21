# Attack log — Linear covering codes of radius two

## 2026-08-16 — q1 (recovered from Codex session 01a009f7-5a24-71e1-bf4c-9667f4d2cbc4)

- Targets tried: $(r,n)=(8,25)$ (documented 26) — best anneal missed 3 of 256 syndromes; CP-SAT/Z3 no model. $(9,38)$ (documented 39) — CP-SAT UNKNOWN; Gabidulin 39-set deletions missed 8.
- Click: seed from the 51-column Kaikkonen–Rosendahl matrix at $r=10$. Fixed-cardinality targeted simulated annealing, xorshift64 run 0, hit 0 uncovered at proposal 3,600,281.
- Witness: 50 distinct nonzero 10-bit columns. F$_2$-rank 10. Exhaustive pair-XOR: 1024/1024. Density $319/256=1.24609375$.
- Commit remembered in Math-agent memory as `5b93f34`. Watcher (Grok, 03:32 PT) independently rebuilt columns from `H_r10_n50.txt` (LSB = row 1) and confirmed 1024/1024.
- $n=49$ stochastic run left 7 uncovered syndromes — not a lower bound.

## 2026-08-16 — q2 (recovered from Codex session 01a00a33-832e-7d13-bf0e-59aeab97ec82)

- Push 50→49 using `H_r10_n50.txt` as seed. Search residue still 7 uncovered. Files: `search_n49.c`, `search_n49_lifted.c`, `build_q2_residue.py`, `verify_q2_residue.py`.
- Do not claim $f(2)$. Holes $(8,25)$ and $(9,38)$ remain secondary.

## 2026-08-16 afternoon — q3 (Claude, `covering-result` branch)

- Built [`result/`](result/) as a self-contained, independently reproducible artifact for the whole result. Run it with `cd problems/covering/result && ./run_all.sh` — 74 checks, exit 0, byte-identical output across runs.
- Two verifiers from scratch, two languages, opposite algorithms: `result/verify/verify.py` is pair-driven, `result/verify/verify.rs` is syndrome-driven. `run_all.sh` diffs their fact dumps. Both re-derive everything from the matrix text; neither reads a stored certificate. A third, quarantined oracle was run only afterwards and agreed on every value; it is not in the tree.
- The missing piece the overnight run never computed: a valid $(2,0)$-partition of $H$ into **10** blocks, against the paper's computer-searched $p(H_{KR})=11$ (arXiv:2511.02542 Thm 5.2). All 973 syndromes that need a pair have a cross-block one; 821 of them have a unique pair, so the partition is tightly forced.
- Minimality: deleting any single column leaves $\ge 9$ uncovered syndromes (best deletions 381, 479, 927 leave exactly 9). So the 50-set is a minimal 1-saturating set in $PG(9,2)$ — an LO code. Not padded.
- $d=3$, exactly 10 dependent triples; exactly one, $(491,734,821)$, spans three distinct blocks (6/4/9). Analogue of Thm 5.2(ii), which is what QM$_5^2$ needs at $r=28$.
- Propagation: Construction QM$_2^2$ (Thm 4.1, eq. (4.2), (4.4)) implemented from the paper. $n_0\ge 2^m\ge p(H_0)$ permits exactly $m=4,5$, asserted not assumed. Results exhaustively verified: $r=18$, $n=815$, 262144/262144; $r=20$, $n=1631$, 1048576/1048576. Published values 831 and 1663.
- These matrices differ from the alternate allocations in [`result/data/alt/`](result/data/alt/) (the indicator allocation is a free choice) and both verify — two distinct witnesses at each $r$, not one.
- Family: $n=51\cdot 2^{r/2-5}-1$, $\bar\mu(2)\le 2601/2048\approx 1.27002$, against the paper's $2704/2048\approx 1.32031$ and the pre-2025 $729/512\approx 1.42383$. Even $r\le 64$ reachable by QM$_2^2$ from this seed: 10, 18, 20, 30–40, 46–64. Not reachable: 12, 14, 16, 22, 24, 26, 28, 42, 44 — the QM$_3^2$/QM$_5^2$ analogues are not implemented and nothing is claimed there.
- Soft spot, stated in the note: only $m=4,5$ are exhaustively verified. The rest of the family inherits the paper's $p(H_C)\le 2^{m+1}+1$ instead of computing partitions. That is the first thing a referee will push on.
- One number in the brief lost to the code: $2601/2048$ is $1.27002$, not $1.26999$. Fraction right, decimal wrong; no bound changes.
- Priority unresolved — Table 5.1 is "best as far as the authors know". Checklist and a drafted email to Davydov/Marcugini/Pambianco in [`result/PRIORITY.md`](result/PRIORITY.md). Nothing goes out before a human works that list.

## 2026-08-18 — q4 (Claude, `cursor/covering-n49-attack-48dc` branch): push 50 → 49

Target: $\ell_2(10,2)\le 49$ — 49 distinct nonzero 10-bit columns, rank 10, singletons + pair-XORs covering all 1024 syndromes. Budget check: $1+49+\binom{49}{2}=1226\ge 1024$, slack 202, density would be $1226/1024\approx 1.19727$. Everything new lives in [`compute/q4/`](compute/q4/); the certified n=50 matrix and `result/` are untouched.

### Angle 1 — symmetry: 49 = 7×7 (new this quest)

If a 49-covering is invariant under a subgroup $G\le GL(10,2)$, it is a union of $G$-orbits, and coverage collapses to orbit-class space (the pair-sum multiset of two orbits is $G$-invariant). For $|G|=7$ the orbit classes number ~147 and a selection is just 7 orbits of size 7 — small enough to exhaust *completely*. Tools:

- [`compute/q4/gen_groups.py`](compute/q4/gen_groups.py) — deterministic generator of subgroup representatives: every cyclic order-$L$ class for $L\in\{3,5,7,9,15,21,35,45,105\}$ as block-diagonal companion matrices (deduped by cyclotomic-coset relabeling under $M\mapsto M^k$), plus $C_7\times C_7$ two-generator groups (orbit sizes 1/7/49). One conjugacy representative suffices: conjugation maps invariant coverings to invariant coverings.
- [`compute/q4/orbit_dfs.c`](compute/q4/orbit_dfs.c) — exhaustive DFS over orbit selections with exact weight 49. Safe prunes only: subset-sum budget DP, an optimistic class-count bound, and suffix reachability masks (a class no remaining single/pair mask can cover kills the branch). Witnesses are re-verified in-process by flat pair enumeration and must still pass the Python verifier.
- Validation: planted-witness tests (direct-sum coverings $W_1^*\cup W_2^*$ are invariant and found at n=62/78), `--no-prune` node-count comparisons, and [`compute/q4/naive_enum.c`](compute/q4/naive_enum.c), an independent dumb enumerator, agreeing on small cases.

Sweep driver: [`compute/q4/run_all_groups.sh`](compute/q4/run_all_groups.sh) → [`compute/q4/orbit_runs.log`](compute/q4/orbit_runs.log). Results so far (each line is an *exhaustive* claim for that subgroup class):

- order-7, trivial part dim 1, blocks $c_1^3$: **no invariant 49-covering** (4.36e9 nodes, 44 s).
- order-7, trivial part dim 1, blocks $c_1^2 c_2$: **no invariant 49-covering** (8.94e9 nodes).
- (sweep continuing: order-7 dim-4/dim-7 fixed spaces, order-9, order-15/21/35/45/105, $C_7\times C_7$ — updated below as they land.)

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

- **Symmetry exhaustions** ([`compute/q4/orbit_runs.log`](compute/q4/orbit_runs.log)): 79 subgroup classes exhausted at n=49, **zero invariant coverings in every one**: all 50 $C_7\times C_7$ classes (orbit sizes 1/7/49 — the "49 = 7×7" resonance is dead for two-generator symmetry), 12 order-15 classes, 10 order-21 classes, 7 order-105 classes, and the two order-7 classes with 1-dimensional fixed space (4.4e9 and 8.9e9 node exhaustions). 11 of the 79 are instant budget infeasibilities (orbit sizes cannot sum to 49, e.g. pure order-3/5/11 actions). **Not settled**: order-7 with fixed-space dim 4 (two classes) and dim 7, plus two order-15 stragglers — timed out at 300–1800 s, no witness seen; and the order-9/-35/-45/-63/-3/-5 files the sweep never reached. Rerun: `CASE_TIMEOUT=big ./compute/q4/run_all_groups.sh` (skips completed cases).
- **k-swap exhaustion**: `best_sa_config` (7 holes) has **no ≤5-swap** to zero holes — exhaustive over all C(49,j) removals, j ≤ 5 (1.9M removal sets, 94.6M re-add nodes, [`compute/q4/kswap5_sa.log`](compute/q4/kswap5_sa.log)). `best_lifted_config` (7 holes): **no ≤4-swap** (j=5 was mid-run when stopped). Prover validated by 4/4 planted controls.
- **Inequivalence**: the two 7-hole optima are *not* GL(10,2)-equivalent despite identical invariant profiles (see Angle 2). At least two distinct deep basins at 7 holes.
- **SAT**: instance built (1.14M clauses), no verdict before stop. [`compute/q4/harvest_optima.sh`](compute/q4/harvest_optima.sh) + [`compute/q4/dedupe_optima.py`](compute/q4/dedupe_optima.py) are ready but unrun.
- Best hole count this quest: **7** (matching q2), now with teeth: provably ≥6-swap-deep (SA config) and two inequivalent basins.
- Certified n=50 matrix and `result/` untouched. Replay: `python3 compute/q4/verify_config.py compute/q4/best_sa_config.cols` (prints the 7 holes); `gcc -O3 ... compute/q4/kswap.c && ./compute/q4/kswap --input compute/q4/best_sa_config.cols --prove 5`; `./compute/q4/orbit_dfs --group compute/q4/groups/<case>.grp --n 49`.
## 2026-08-19 — q5 (Codex, QM$_3^2$/QM$_5^2$ propagation)

- The direct and lifted 49-column searchers ran concurrently for 1228.66 seconds each (7 and 8 threads, all documented modes, master seeds `0x49A202608190001` and `0x49B202608190002`). A new guided add-then-delete/breakout search in [`compute/search_n49_guided.c`](compute/search_n49_guided.c) ran 637.74 seconds on 4 threads. All three best checkpoints independently recount to rank 10, 49 distinct nonzero columns, and 1017/1024 covered: **7 uncovered remains a search residue, not a lower bound**. Checkpoints: `compute/q2_direct_20260819_a.json`, `compute/q2_lifted_20260819_a.json`, `compute/q2_guided_20260819_a.json`.
- Construction QM$_3^2$ (arXiv:2511.02542 Thm. 5.1) was implemented deterministically in [`compute/build_qm3.py`](compute/build_qm3.py). The seed's 10-block partition is rechecked, the field polynomials are checked for irreducibility, and the matrices are independently checked from text by [`compute/verify_radius2_matrix.c`](compute/verify_radius2_matrix.c). Certified new bounds: $\ell_2(22,2)\le3325$ (paper: 3389), $\ell_2(24,2)\le6653$ (paper: 6781), and $\ell_2(26,2)\le13309$ (paper: 13565). Exhaustive coverage was 4194304/4194304, 16777216/16777216, and 67108864/67108864, respectively; all matrices have full rank and distinct nonzero columns.
- For QM$_5^2$, [`compute/build_qm5.py`](compute/build_qm5.py) refines the seed partition to 16 blocks and isolates the already-certified cross-block triple $(491,734,821)$. Its alternative $r=18,n=815$ lift has an explicit, exhaustively checked 33-block partition; this is an intermediate tailored to QM$_5^2$, **not a re-claim of the existing $r=18$ bound**. The resulting `compute/H_r28_n26111.txt` has rank 28, 26111 distinct nonzero columns, and exhaustive coverage 268435456/268435456. Its explicit 66-block partition also covers 268435456/268435456 syndromes using only cross-block pairs. Thus $\ell_2(28,2)\le26111$, improving the paper's 26623 by 512.
- The verified $p(H)\le66$ at $r=28$ satisfies the QM$_2^2$ hypothesis $26111\ge2^m\ge66$ for $m=7,8$. The theorem therefore gives $\ell_2(42,2)\le3342335$ and $\ell_2(44,2)\le6684671$, improving 3407871 and 6815743. These two large continuations are theorem-propagated from the exhaustively checked matrix/partition; no claim is made that their $2^{42}$ or $2^{44}$ syndrome spaces were enumerated.
- Reproduction: run `compute/run_qm3_checks.sh` and `compute/run_qm5_checks.sh` from this problem directory. The builders also reproduced every matrix and partition byte-for-byte in a fresh directory. No optimality or $f(2)$ claim is made.

## 2026-08-19 — q6b (Codex, exact 3-sums, QM$_5^3$, and $p\le64$)

- The requested Lemma 7.5 analogue holds in a stronger exact form: **every one of the 1024 vectors of $\mathbb F_2^{10}$ is the sum of exactly three distinct columns** of `compute/H_r10_n50.txt`. The standalone [`compute/verify_three_sum.c`](compute/verify_three_sum.c) reparses the matrix and independently obtains rank 10, 50 distinct nonzero columns, `exact3=1024/1024`, and `two_or_three=1024/1024` after enumerating all $\binom{50}{3}=19600$ triples.
- [`compute/build_qm35.py`](compute/build_qm35.py) implements Construction QM$_5^3$ of arXiv:2511.02542, Thm. 7.3 (called QM$_3^5$ in the q6b brief). It constructs a parity check matrix of the cyclic perfect Golay $[23,12,7]_2$ radius-3 code from generator polynomial `0xAE3`, exhausts its 4095 nonzero codewords and 2048 syndromes, and glues the certified 50-column radius-2 matrix as $D_4$ with $m=5$. The explicit output [`compute/H_R3_r26_n817.txt`](compute/H_R3_r26_n817.txt) has rank 26 and 817 distinct nonzero columns. The independent matrix-only [`compute/verify_radius3_matrix.c`](compute/verify_radius3_matrix.c) enumerates 333336 pairs and 90556280 triples from the text: 321719/67108864 syndromes are covered at radius 2 and **67108864/67108864 at radius 3**. Therefore $\ell_2(26,3)\le817$, improving the paper's 818 by one.
- The constructive 66-block partition of the already-certified $r=28,n=26111$ radius-2 matrix can be coarsened. [`compute/search_partition_merges.c`](compute/search_partition_merges.c) exhaustively classifies each of all $2^{28}$ syndromes as having one, two, or at least three distinct block-pair representations (with zero and singleton syndromes protected). It proves that the disjoint merges of original blocks `0+3` and `1+4` are jointly safe and writes [`compute/partition_r28_n26111_p64.txt`](compute/partition_r28_n26111_p64.txt). The older independent [`compute/verify_radius2_matrix.c`](compute/verify_radius2_matrix.c) then reparses the matrix and new labels and confirms rank 28, 26111 distinct nonzero columns, and **268435456/268435456 cross-block-covered syndromes with 64 blocks**. Thus $p(H)\le64$; no minimality of 64 is claimed.
- The verified $p(H)\le64$ unlocks QM$_2^2$ at $m=6$: $26111\ge64\ge p(H)$, so the theorem gives $\ell_2(40,2)\le64(26111+1)-1=1671167$, improving the paper's 1703935 by 32768. This $r=40$ continuation is theorem-propagated from the exhaustively checked matrix and partition; its $2^{40}$ syndrome space was not enumerated.
- Reproduction: run [`compute/run_qm35_checks.sh`](compute/run_qm35_checks.sh) and [`compute/run_p64_checks.sh`](compute/run_p64_checks.sh) from this problem directory. `result/` was read only and remains untouched. No claim of optimality or $f(2)$ is made.

## 2026-08-19 — q6c (Codex, explicit QM$_4^4$ certificate)

- [`compute/build_qm44.py`](compute/build_qm44.py) implements Construction QM$_4^4$ of arXiv:2511.02542, Thm. 9.1, with odd $m=5$. It reconstructs the Östergård–Kaikkonen $[19,8]_2$ radius-4 seed $H_{OK2}=[I_{11}\ M_{OK2}]$, gives its 19 singleton blocks the distinct nonzero $\mathbb F_{32}$ indicators `1..19`, and uses the certified `H_r10_n50.txt` in $D_5$. The explicit output [`compute/H_R4_r31_n689.txt`](compute/H_R4_r31_n689.txt) has $r=11+4\cdot5=31$ and $n=32\cdot19+50+31=689$.
- The seed hypothesis is certified rather than inferred from the length formula. Exhaustive enumeration in $\mathbb F_2^{11}$ gives cumulative OK2 coverage `20, 183, 981, 2048` at weights 1 through 4. The dependent triple $h_9+h_{10}+h_{14}=0$ supplies a nonempty representation of zero. [`compute/qm44_top_certificate.txt`](compute/qm44_top_certificate.txt) records a nonempty sum of 1–4 distinct singleton blocks for every one of the 2048 top syndromes; its weight histogram is `19, 163, 799, 1067`.
- The independent C verifier [`compute/verify_qm44.c`](compute/verify_qm44.c) shares no source with the Python builder. It reparses both matrices and the certificate, checks rank 31 and 689 distinct nonzero columns, matches every parsed column against the $D_5$ or $A(h,\beta)$ identity over $\mathbb F_{32}=\mathbb F_2[x]/(x^5+x^2+1)$, exhausts all 1024 syndromes of the radius-2 constituent, checks all 31 Hamming columns, and verifies all 2029 finite-field maps used by the weight-2/3/4 cases are invertible. It additionally constructs and checks 53,248 witnesses directly against the matrix text.
- This is a complete blockwise certificate for all $2^{31}$ syndromes, not a flat $2^{31}$-bit sweep. Weight 4 uses an invertible $4\times4$ Vandermonde map; weight 3 leaves one $W_5$ column; weight 2 leaves a radius-2 constituent syndrome; weight 1 leaves at most two constituent columns and one $W_5$ column. Conversely, 1067 OK2 top syndromes are not sums of at most three seed columns, so projection proves the output radius is exactly 4. A lifted dependent triple and projectivity give minimum distance exactly 3. Therefore the explicit $[689,658,3]_2^4$ code proves the new table dent $\ell_2(31,4)\le689$, improving the paper's 690 by one; no optimality is claimed.
- Reproduction: run [`compute/run_qm44_checks.sh`](compute/run_qm44_checks.sh) from this problem directory. A clean rebuild was byte-identical, GCC AddressSanitizer/UBSan passed, and one-bit matrix and one-entry certificate mutations were both rejected. SHA-256: matrix `4e7ecff7fe1a293fd50516171ad035376cbcc65c9347958fee4b00b6eb9c9164`; top certificate `2f5fe5b2ef6f46804516736a99d6fa3fac4f858a42b8e3a9b139d3e7254b7870`. `result/` and the q6a search were untouched.

## 2026-08-19 — q7c (Codex, explicit lift partitions and honest QM$_5^3$ continuations)

- [`compute/build_lift_partitions.py`](compute/build_lift_partitions.py) reconstructs the canonical `result/data/H_r18_n815.txt` and `result/data/H_r20_n1631.txt` matrices column-for-column from the certified 50-set and its 10-block partition. It first implements the constructive partition in the proof of Theorem 5.4: the $2^m$ interim $\beta$-blocks are split by $\xi=0$ versus $\xi\ne0$, and $D_1(2)$ is the last block. This gives the explicit 33- and 65-block certificates [`compute/partition_r18_n815.txt`](compute/partition_r18_n815.txt) and [`compute/partition_r20_n1631.txt`](compute/partition_r20_n1631.txt).
- Static coarsening maps then give [`compute/partition_r18_n815_p17.txt`](compute/partition_r18_n815_p17.txt) and [`compute/partition_r20_n1631_p14.txt`](compute/partition_r20_n1631_p14.txt). The older, independent C checker [`compute/verify_radius2_matrix.c`](compute/verify_radius2_matrix.c) reparses each matrix and label file and confirms full rank, 815/1631 distinct nonzero columns, and respectively **262144/262144 cross-block-covered syndromes with 17 blocks** and **1048576/1048576 with 14 blocks**. Thus $p(H_{18})\le17$ and $p(H_{20})\le14$; no minimality is claimed. The proof-constructed 33/65 parents are also independently swept.
- For each large radius-3 lift, [`compute/verify_qm35_identity.py`](compute/verify_qm35_identity.py) checks every hypothesis of arXiv:2511.02542, Theorem 7.3. It independently certifies the 23-column Golay matrix as a perfect $[23,12,7]_2$ code and its singleton $(3,0)$-partition by enumerating all 2048 distinct weight-at-most-three syndromes. It exhaustively certifies the radius-2 constituent and its explicit 17- or 14-block 2-partition. It checks $m\ge2$, $\mathscr B=\{1,\ldots,23\}\subset\mathbb F_{2^m}^{*}$, $23\le2^m-1$, irreducibility of the field polynomial, full output rank and projectivity, and every emitted $D_4$ and $A(h,\beta)$ column identity.
- With $m=9$ and $V_{18}$ of length 815, the explicit matrix [`compute/H_R3_r38_n13102.txt`](compute/H_R3_r38_n13102.txt) has $r=11+3m=38$ and $n=2^m(23+1)+815-1=13102$. With $m=10$ and $V_{20}$ of length 1631, [`compute/H_R3_r41_n26206.txt`](compute/H_R3_r41_n26206.txt) has $r=41$ and $n=26206$. Theorem 7.3 therefore proves $\ell_2(38,3)\le13102$ and $\ell_2(41,3)\le26206$, improving the paper's 13118 and 26238 by 16 and 32. These are theorem-only covering certificates; no $2^{38}$ or $2^{41}$ flat sweep is claimed or performed.
- Reproduction: run [`compute/run_q7c_checks.sh`](compute/run_q7c_checks.sh). It regenerates and independently sweeps the four partition certificates, rebuilds only the two new large matrices in a temporary directory and compares them byte-for-byte, then rechecks all Theorem 7.3 hypotheses and construction identities. `result/` is read only. No optimality or $f(2)$ claim is made.

## 2026-08-20 — leftover unused paper constructions (QM$_2^1$, QM$_4^3$)

- [`compute/recover_mok.py`](compute/recover_mok.py) treats the printed last $M_{OK}$ word `ICE` as OCR. Preferred `1CE` is the unique 9-bit last column that makes $H_{OK}=[I_9\ M_{OK}]$ a rank-9 projective $[18,9]_2$ code of covering radius exactly 3 whose Theorem 7.1 partition $P_{OK}$ is a $(3,1)$-partition of $\mathbb F_2^9$. Dependent triple $h_6+h_9+h_{16}=0$ is in three distinct blocks.
- [`compute/build_qm43.py`](compute/build_qm43.py) implements Construction QM$_4^3$ (Thms 6.4, 7.1–7.2) with $m=4$, $D=D_3$, and $\mathscr B=\mathbb F_{16}\cup\{*\}$. Output [`compute/H_R3_r21_n303.txt`](compute/H_R3_r21_n303.txt) has $r=21$, $n=303$. Independent identity checker [`compute/verify_qm43_identity.py`](compute/verify_qm43_identity.py); covering certificate is the existing matrix-only C sweep of all $2^{21}$ syndromes.
- [`compute/build_qm21.py`](compute/build_qm21.py) implements Construction QM$_2^1$ (Thm 4.1 / (4.1), (4.3)) on the certified $r=18$, $n=815$ matrix and its 17-block partition. $2^4+1=p(H_{18})$. Output [`compute/H_r26_n13070.txt`](compute/H_r26_n13070.txt) has $r=26$, $n=16\cdot(815+2)-2=13070$, against the paper's 13565 and the previous certified 13309. Independent identity checker [`compute/verify_qm21_identity.py`](compute/verify_qm21_identity.py). The existing C verifier covers **67108864/67108864** syndromes in 0.460 s, so $\ell_2(26,2)\le 13070$.
- Putting both $D_2(2)$ Hamming copies into the star seed-block misses 9105 syndromes. Giving each Hamming copy its own block yields the explicit 19-block 2-partition [`compute/partition_r26_n13070_p19.txt`](compute/partition_r26_n13070_p19.txt); the same C verifier covers 67108864/67108864 using only cross-block pairs. Thus $p(H_{26})\le 19$. This unlocks QM$_2^2$ at $m=5$ ($13070\ge 32\ge 19$), so theorem-only $\ell_2(36,2)\le 32\cdot 13071-1=418271$, against the paper's 425983. The $2^{36}$ space was not enumerated.
- Reproduction: [`compute/run_qm43_checks.sh`](compute/run_qm43_checks.sh) and [`compute/run_qm21_checks.sh`](compute/run_qm21_checks.sh). `result/` is read only. No optimality or $f(2)$ claim is made. No $n=49$ search.

## 2026-08-20 — q8c (Codex, exact recursive coarsening at $r=28$)

- Starting from the certified 64-block partition of `compute/H_r28_n26111.txt`, [`compute/search_partition_merges.c`](compute/search_partition_merges.c) was applied recursively. At every step it exhaustively classified all $2^{28}$ syndromes by their surviving block-pair representations before accepting two safe disjoint merges. The deterministic chain reached $64,62,\ldots,30,28$ blocks; its exact merge choices are recorded in [`compute/build_p28_partition.py`](compute/build_p28_partition.py).
- The resulting explicit certificate [`compute/partition_r28_n26111_p28.txt`](compute/partition_r28_n26111_p28.txt) has 26,111 labels in 28 nonempty blocks. The pre-existing, independent C verifier reparsed the matrix and labels, checked rank 28 and 26,111 distinct nonzero columns, enumerated all 340,879,105 unordered pairs, and confirmed **268435456/268435456 cross-block-covered syndromes**. Thus $p(H_{28})\le28$, improving the previously certified $p(H_{28})\le64$; no partition minimality is claimed.
- Since $26111\ge2^5=32\ge28$, QM$_2^2$ is now directly legal from this $r=28$ matrix at $m=5$. It gives $r=38$ and $n=32(26111+1)-1=835583$, an alternative direct derivation of the already recorded $r=38$, radius-2 family value. The new dent here is the explicit $p(H_{28})\le28$ certificate, not a new numerical $r=38$ table bound.
- Reproduction: run [`compute/run_p28_checks.sh`](compute/run_p28_checks.sh). It rebuilds the partition in a temporary directory, requires byte identity with the tracked certificate, runs the independent exhaustive verifier, and checks the QM$_2^2$ arithmetic. `result/` is untouched. No claim of optimality or $f(2)$ is made.

## 2026-08-20 — odd-r Table 5.1 holes (wrap: residue only)

Hard wrap. No shorter radius-2 matrix. Paper lengths still \(\ell_2(11,2)\le 79\) and \(\ell_2(13,2)\le 159\). No \(f(2)\) claim.

- Rebuilt the GDT \(f(r)\) seed ([`compute/build_gabidulin.py`](compute/build_gabidulin.py)): \(m=6\) is an explicit 79-set covering \(2048/2048\); \(m=7\) is a 159-set covering \(8192/8192\). These reconstruct the table, they do not dent it.
- Every 1-deletion of the 79-set leaves \(16,29,30,36,\) or \(64\) holes. The four 16-hole punctures are [`compute/odd_r11_n78_16hole_a.cols`](compute/odd_r11_n78_16hole_a.cols) and siblings. Exhaustive 1-swap on puncture \(a\) stays at 16 holes.
- No 2-out-1-in replacement from that 79-set reaches 0 holes (best 2-deletion leftover: 34).
- Compiled SA at \(n=78\) did not find a covering. Residues: 16 holes from a Gabidulin puncture; 37 holes from a 78-subset of a longer union-greedy set. See [`compute/odd_r_residue_2026-08-20.json`](compute/odd_r_residue_2026-08-20.json).
- \(r=13\) 1-deletions of the 159-set leave 32–128 holes; no \(n=158\) run finished before wrap.


## 2026-08-21 — q9 (Claude Opus 5, `fable/covering-n49-traj`): trajectory of the $r=10$ record, and exact quotient-block replacement

**No 49-covering. No dent.** Everything below is a recovered artifact, a
verified structural fact about the published solutions, or certified search
residue. `result/` was read only; no q2/q4 search (SA, guided, lifted, k-swap,
invariant orbit DFS) was rerun. New material is in [`compute/q9/`](compute/q9/).

### History first

- **The Kaikkonen–Rosendahl 51-set is recovered.** RESEARCH.md had recorded the
  explicit 51-column listing as never obtained. It is reprinted as display
  (4.9) of arXiv:2511.02542v1 (their Thm 4.3, citing Kaikkonen–Rosendahl,
  *New covering codes from an ADS-like construction*, IEEE Trans. Inform.
  Theory **49**(7) 1809–1812, 2003, p. 1812) as 41 hexadecimal columns with
  $H_{KR}=[I_{10}\ M_{KR}]$. Transcribed in
  [`compute/q9/build_kr51.py`](compute/q9/build_kr51.py), rebuilt as
  [`compute/q9/H_r10_n51_KR.txt`](compute/q9/H_r10_n51_KR.txt): rank 10, 51
  distinct nonzero columns, exhaustive pair-XOR **1024/1024**.
- **The trajectory, re-derived rather than copied**
  ([`compute/q9/trajectory.py`](compute/q9/trajectory.py)): 53 (1992,
  $\phi(10)=27\cdot2^{t-4}-1$, Davydov–Drozhzhina-Labinskaya / CHLL
  Thm 5.4.27(i)) → 51 (2003, Kaikkonen–Rosendahl, $-2$) → 51 (Nov 2025, still
  the Table 5.1 entry of arXiv:2511.02542, and their lift seed) → 50 (q1,
  2026-08-16, $-1$) → 49 open. Densities $179/128$, $1327/1024$, $319/256$,
  $613/512$. Volume bound only gives $n\ge45$.
- **53 is a lift; 51 and 50 are not.** $\phi$ doubles $n+1$ every two units of
  $r$, so its $r=10$ entry is literally the $r=8$ entry carried up,
  $2(26+1)-1=53$. Against that,
  [`compute/q9/profiles.py`](compute/q9/profiles.py) sweeps all **174251**
  two-dimensional quotients $q:\mathbb F_2^{10}\to\mathbb F_2^2$ of both the
  51-set and the 50-set: **no** quotient of either has its kernel block
  $S\cap\ker q$ covering $\ker q$. Both are quotient-flat — kernel-block size
  stays in $3..27$ (51-set) and $3..26$ (50-set) around a mean of $n/4$.
  So the "improve the $r=8$ seed and re-lift" reading of the table died in 2003
  and the 49 is not going to come from it.

### The construction family that follows from that

Fix a quotient with kernel $V$ and coset representatives $t_{00}=0,t_{01},t_{10},
t_{11}=t_{01}+t_{10}$ (this choice kills the twist). Pulling the four blocks
$(A;B,C,D)$ back into $V$, covering radius $\le2$ is *equivalent* to

$$
\begin{aligned}
(00)&\ \{0\}\cup A\cup\Delta(A)\cup\Delta(B)\cup\Delta(C)\cup\Delta(D)=V,\\
(01)&\ (A\cup\{0\})+B\ \cup\ C+D=V,\qquad (10),(11)\ \text{the label-permuted twins},
\end{aligned}
$$

with $\Delta(X)=\{x+x':x\ne x'\}$.
[`compute/q9/verify_blocks.py`](compute/q9/verify_blocks.py) checks this
equivalence in both directions against a direct syndrome sweep on the 51-set,
the 50-set and both 7-hole residues, matching the exact hole *sets*, on 160
quotient instances.

Freeze $A,B,C$: every condition on $D$ becomes a hitting-set constraint
($u\notin A^{+}+B\Rightarrow D\cap(u+C)\ne\emptyset$, and twins) plus one pair
constraint ($h\in\Delta(D)$ for each syndrome the other three blocks miss). So
*"is there **any** block of size $\le k$ finishing $A,B,C$?"* is exactly
decidable. [`compute/q9/block_solve.c`](compute/q9/block_solve.c) decides it by
constraint-directed DFS: sibling exclusion on the hitting branches, where the
branches really are "$d\in D$" and partition the space; deliberately no
exclusion on the pair branches, where they overlap and exclusion would be
unsound; counting prunes on all four families.

**This is not a $k$-swap.** A block carries up to 18 columns, all re-chosen at
once and exactly. `--shrink` asks for a block one column shorter (turning the
certified 50-set into a candidate 49); `--resolve` asks for one the same size
(turning a 7-hole 49-residue into a candidate covering).

### Controls

- Encoding, positive: `--resolve` on the certified 50-set returns a valid 50 on
  the first instance, re-verified 1024/1024 by an independent flat sweep.
- Reduction, both directions: 160 quotient instances, exact hole sets agree.
- **Planted, 7/7.** Erase an entire block of the certified 50-set, replace it
  with uniformly random kernel elements, ask the solver to rebuild one. All
  seven recovered, at block sizes 8, 8, 10, 11, 12, 13, 14, each re-verified
  1024/1024. A needle at depth **14** is found; q4's exhaustive prover reached
  depth 5.
- Independent oracle: `--selftest k` cross-checks the DFS verdict against
  brute-force enumeration of every candidate block of size $\le k$, scored only
  by the flat covering test, sharing no code with the constraint encoding.

### Sweeps (node cap 20000 per instance, `--maxblock 18`)

Each sweep covers all 174251 quotients $\times$ 3 non-kernel blocks = 522753
instances. `skipped` = block wider than `--maxblock`; `capped` = node cap hit,
which is **unknown, not a negative**; `decided` = search tree exhausted, an
exact exclusion.

| sweep | instances | decided | capped (unknown) | skipped | result |
| --- | --- | --- | --- | --- | --- |
| `--shrink` on the certified 50-set (asks for 49) | 509468 | 220118 | 289350 | 13285 | no completion |
| `--resolve` on `best_sa_config` (7 holes) | 514224 | 156264 | 357960 | 8529 | no completion |
| `--resolve` on `best_lifted_config` (7 holes) | 514160 | 164382 | 349778 | 8593 | no completion |
| `--shrink` on the KR 51-set (asks for 50) | 507792 | 159279 | 348513 | 14961 | no completion |

A second, deeper pass restricted to narrow blocks (`--maxblock 12`, node cap
200000) leaves almost nothing undecided:

| sweep | instances | decided | capped (unknown) | skipped | result |
| --- | --- | --- | --- | --- | --- |
| `--shrink` on the certified 50-set, blocks $\le 12$ | 279034 | **271127 (97.2%)** | 7907 | 243719 | no completion |

That row is the strongest single statement of the quest: for every one of the
174251 quotients and every non-kernel block of at most 12 columns, replacing
that whole block by any shorter block is decided — and 97.2% of the time the
answer is exhaustively no. Not one instance produced a 49.

**Calibration, and a limit of the move class.** `--shrink` on the 2003 51-set
does *not* find a 50 either. The 51→50 step that q1 actually made by annealing
is therefore not a single-quotient-block shrink (at least not among the 159279
decided instances). The block move is far larger than a $k$-swap — planted
needles at depth 14 are found — but it is not a superset of what annealing did,
and that is worth knowing before anyone reads a negative here as evidence about
49.

So: **220118 exact decisions** say the certified 50-set cannot be shortened by
replacing any one of those quotient blocks with a shorter block, and 320646
exact decisions say neither 7-hole optimum can be repaired by replacing any one
of those blocks. Between them that is over half a million simultaneous
rearrangements of up to 18 columns, ruled out one at a time — and roughly 57%
of the instances were left undecided by the node cap. **None of this is a lower
bound.** $\ell_2(10,2)=49$ remains open.

### Replay

    cd problems/covering
    python3 compute/q9/build_kr51.py compute/q9/H_r10_n51_KR.txt
    python3 compute/q9/trajectory.py
    python3 compute/q9/profiles.py compute/q9/H_r10_n51_KR.txt compute/H_r10_n50.txt
    python3 compute/q9/verify_blocks.py compute/H_r10_n50.txt 40
    gcc -O2 -o /tmp/bs compute/q9/block_solve.c
    /tmp/bs --input compute/H_r10_n50.txt --shrink --maxblock 18 --nodes 20000 --shard 0/4

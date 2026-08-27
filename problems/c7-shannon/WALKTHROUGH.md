# How a Fifth-Power Record Did Not Move

## 0. What was actually missing

The capacity number $\Theta(C_7)$ already moved in July 2026, but only through gadgets in the 10th and 200th strong powers. The fifth-power independence number is a different finite object: a subset of $(\mathbb Z/7\mathbb Z)^5$ in which every pair has circular distance $>1$ in some coordinate. The published maximum is still 367. The missing degree of freedom is one extra vertex, or a certificate that none exists.

A 368-set is already a new bound. Its fifth root is about 3.2596, which would also beat the Lean-verified 3.258805, but that comparison is not required to count the finite set.

## 1. Named false starts

**Direct homomorphism.** If some cyclic orbit of size $n\ge 368$ has min-max circular distance $k\ge 2n/7$, the floor map lands in $C_7$ and we are done. Exhaustive geometric search on $n=300..600$, and random generators on $n=368..400$, never cleared the threshold. The famous $382/108$ ratio is 3.537, still above 3.5. The closest miss was $n=317$, $q=31$, $k=90$ versus need 91 — and 317 is too small anyway.

**Linear codes.** A good 3-dimensional $\mathbb F_7$-subspace has size 343. Thirty random good codes had empty residual: you cannot add even one extra point. The 24-point gap from 343 to 367 is nonlinear. Eight cosets of a good $2$-dimensional code would have been $392$. Every good $2$-dimensional code is now decided: the $343$-vertex quotient has $\alpha\le 7$. Seven cosets are $343$ and leave no original-graph residual.

**Maximum independent set of the folded orbit.** Polak–Schrijver throw away every non-isolated image vertex (55 of them). Keeping an MIS of that conflict graph instead produces a larger core (357) but a residual of only 4, total 361. The 40-vertex leftover they kept is worth more than those 30 conflict vertices.

**Small swaps.** The 367-set is maximal (0 free vertices). Exhaustive 1-out, 2-out, and 3-out searches have gain 0. That matches the paper's 3-out/4-in report and extends it to a complete 3-out census (8,171,255 triples).

**Few-flip SAT (stolen from W(2,7)).** Cadical with library `CardEnc.atmost` refuted every odd Hamming distance $\le 9$ from the seed, so 4-out/5-in is also empty. Hamming $11$ is now finished as well: every $5$-out/$6$-in that adds a $4$- or $5$-blocker vertex frees at most $11$ candidates with $\alpha\le 4$, and the leftover SAT on $\le 3$-blocker candidates is UNSAT. Hamming $13$ is empty in the $5$- and $6$-blocker cases (freed $\alpha\le 4$). That is still a ball around one seed, not $\alpha\le 367$.

**Four-letter local search.** Growing the $367$-set inside a $4$-letter slice reached $309$. That number is irrelevant: a $4$-support set cannot reach $368$ at all.

**Product template.** $10\times 33=330$ is already a maximal independent set. CEGAR cannot grow it. A template can be leftover-free and still 38 short.

**Missing a letter.** Baumert et al. give $\alpha(C_7^{\boxtimes 4})\le 115$. An adjacent pair of letters in one coordinate induces $K_2\boxtimes C_7^{\boxtimes 4}$ and contributes at most $115$, not $230$, because the two fibers project to one independent set in the fourth power. Every $1$--$6$ letter support therefore has size at most $345$. A $368$-set uses all seven letters in every coordinate.

**Two translates of the 367-set.** For every nonzero $v\in(\mathbb Z/7\mathbb Z)^5$, the bipartite matching on $A\setminus(A+v)$ versus $(A+v)\setminus A$ is perfect, so $\alpha(A\cup(A+v))=367$. That shape is closed.

**A 5-fiber of the published 6th- or 10th-power sets.** Itty's 1120-set in dimension 6 has max 5-fiber 165. The 10th-power gadget built from the 367-set has max 5-fiber 367.

## 2. The useful failure

The isolate/residual split is a real tradeoff, not a sloppy deletion. The 327 isolates leave a 71-vertex, 85-edge residual whose independence number is 40. Eating the conflict vertices first spends that leftover. Any attempt to beat 367 has to change the 327-core, not just re-pack the 71. Puncturing one isolate and re-solving the residual always returned $\alpha=41$, total 367: the extra leftover vertex exactly replaces the one that was deleted.

Orbit ratios also taught a negative: among geometric progressions, $n=382$, $q=7$ is still the closest approach to $7/2$ in the range that could matter. Folding the nearer-ratio $n=317$ orbit into seven symbols explodes the residual and yields totals around 250.

Hoffman on the $8$-coset Cayley graphs was the other useful miss. The graphs are regular of degree $122$–$228$, and the smallest eigenvalue is negative enough that the Hoffman number sits around $33$. A spectral bound that looks like it should kill $\alpha<8$ does not even touch $8$. The leftovers were a node cap, not a hard family.

## 3. The click

The pair-fiber projection. Two adjacent letters look like they should give $115+115$, but $(0,x)$ is adjacent to every $(1,y)$ in the closed neighbourhood of $x$, so the two fibers cannot both be large. They fold to a single independent set in $C_7^{\boxtimes 4}$. Once that is visible, missing even one letter in one coordinate is fatal for $368$. The published translation $(40,123,40,123,40)$ before the fold $\lfloor 2i/109\rfloor$ remains the best completed construction. Other translations of the same orbit scored 357–360.

## 4. The argument, in the order it was found

Seed first. The Itty ancillary `R367.txt` is the Polak–Schrijver appendix. A pairwise verifier checks circular distance $>1$ in some coordinate; it accepts the 367-set. Reconstruction from the circular orbit independently reproduces $|M|=327$, residual $71/85$, $\alpha=40$.

Then the homomorphism search, the S' MIS, the swap census, the linear residuals, and the fold/shift reruns. None produced 368.

The pair-fiber bound came later, while trying to finish the $4$-support search that had been left as a local grow. Hamming $11$ was the other leftover from the few-flip ball. The $8$-coset census looked unfinished because $1280$ graphs hit an $80000$-node cap. Deduplicating the connection sets dropped $97240$ codes to $9584$ Cayley graphs; a complete search on those unique graphs found no $8$-pack.

## 5. Computer search

- `compute/R367.txt` — published 367-set, verifier OK
- `compute/R_reconstructed.txt` — pipeline 367-set, verifier OK, differs in 2 vertices
- `compute/R361_sprime.txt` — S' MIS construction, size 361, verifier OK
- `compute/verify_set.py` — pairwise checker
- logs: `orbit_search_wide.txt`, `three_out_log.txt`, `fold_near.txt`, `linear_probe.txt`, `local_search_log.txt`, `fewflip_sat_log.txt`, `minconflicts_cage.txt`, `cegar_product_log.txt`
- `compute/q1/` — six-shape search: translate matching (complete, $\alpha=367$ for every $v$), private-pair 2-out plateau (`best_gain=0` on 108 seeds), isolate-core $k=1$ census (327/327 at total 367), 4-support local best 309, verified 120 good 2-dimensional codes with at most 7 cosets, higher-power fiber replay (165 and 367)
- `compute/q2/bound_support.py` — $126$ supports of size $1$--$6$, all $\le 345$; pair projections of the $367$-set independent
- `compute/q2/hamming11_log.txt`, `hamming11_sat_log.txt` — Hamming $11$ empty
- `compute/q2/coset_exact_log.txt` — $140050$ subspaces, $97240$ good, no $8$-pack; $1280$ leftover graphs after a second pass (`coset_unknown_c_log.txt`)
- `compute/q3/coset_finish_log.txt` — $9584$ unique connection sets, clique cover $359$, exact search $9225$, leftover $0$
- `compute/q3/unique_sample_log.txt` — Python RREF count and Cadical sample of $159$ unique graphs, all UNSAT
- `compute/q3/hamming13_log.txt` — Hamming $13$ cases A+B empty (`best_mis=4`)

## 6. What is proved vs still open

The 367-set is independent. $\alpha(C_7^{\boxtimes 5})\ge 367$ is old. This search did not find 368 and did not prove 367 is maximum. An independent set that misses a letter in any coordinate has size at most $345$. Hamming distance $11$ from the published $367$-set contains no $368$-set. The union of the published set with any translate has independence number 367. No good $2$-dimensional $\mathbb F_7$-code has eight independent cosets. Hamming $13$ is empty when an added vertex has $5$ or $6$ blockers; the $\le 4$-blocker slice is residue. Lovász still gives $\alpha\le 401$. $\Theta(C_7)$ is not claimed from this folder.

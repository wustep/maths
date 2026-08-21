# How a Fifth-Power Record Did Not Move

## 0. What was actually missing

The capacity number $\Theta(C_7)$ already moved in July 2026, but only through gadgets in the 10th and 200th strong powers. The fifth-power independence number is a different finite object: a subset of $(\mathbb Z/7\mathbb Z)^5$ in which every pair has circular distance $>1$ in some coordinate. The published maximum is still 367. The missing degree of freedom is one extra vertex, or a certificate that none exists.

A 368-set is already a dent. Its fifth root is about 3.2596, which would also beat the Lean-verified 3.258805, but that comparison is not required to count the finite set.

## 1. Named false starts

**Direct homomorphism.** If some cyclic orbit of size $n\ge 368$ has min-max circular distance $k\ge 2n/7$, the floor map lands in $C_7$ and we are done. Exhaustive geometric search on $n=300..600$, and random generators on $n=368..400$, never cleared the threshold. The famous $382/108$ ratio is 3.537, still above 3.5. The closest miss was $n=317$, $q=31$, $k=90$ versus need 91 — and 317 is too small anyway.

**Linear codes.** A good 3-dimensional $\mathbb F_7$-subspace has size 343. Thirty random good codes had empty residual: you cannot add even one extra point. The 24-point gap from 343 to 367 is nonlinear.

**Maximum independent set of the folded orbit.** Polak–Schrijver throw away every non-isolated image vertex (55 of them). Keeping an MIS of that conflict graph instead produces a larger core (357) but a residual of only 4, total 361. The 40-vertex leftover they kept is worth more than those 30 conflict vertices.

**Small swaps.** The 367-set is maximal (0 free vertices). Exhaustive 1-out, 2-out, and 3-out searches have gain 0. That matches the paper's 3-out/4-in report and extends it to a complete 3-out census (8,171,255 triples).

**Few-flip SAT (stolen from W(2,7)).** Cadical with library `CardEnc.atmost` refuted every odd Hamming distance $\le 9$ from the seed, so 4-out/5-in is also empty. That is still a ball around one seed, not $\alpha\le 367$.

**Product template.** $10\times 33=330$ is already a maximal independent set. CEGAR cannot grow it. A template can be leftover-free and still 38 short.

## 2. The useful failure

The isolate/residual split is a real tradeoff, not a sloppy deletion. The 327 isolates leave a 71-vertex, 85-edge residual whose independence number is 40. Eating the conflict vertices first spends that leftover. Any attempt to beat 367 has to change the 327-core, not just re-pack the 71.

Orbit ratios also taught a negative: among geometric progressions, $n=382$, $q=7$ is still the closest approach to $7/2$ in the range that could matter. Folding the nearer-ratio $n=317$ orbit into seven symbols explodes the residual and yields totals around 250.

## 3. The click

There was no click. The published translation $(40,123,40,123,40)$ before the fold $\lfloor 2i/109\rfloor$ remains the best completed score. Other translations of the same orbit scored 357–360.

## 4. The argument, in the order it was found

Seed first. The Itty ancillary `R367.txt` is the Polak–Schrijver appendix. A pairwise verifier checks circular distance $>1$ in some coordinate; it accepts the 367-set. Reconstruction from the circular orbit independently reproduces $|M|=327$, residual $71/85$, $\alpha=40$.

Then the homomorphism search, the S' MIS, the swap census, the linear residuals, and the fold/shift reruns. None produced 368.

## 5. Computer residue

- `compute/R367.txt` — published 367-set, verifier OK
- `compute/R_reconstructed.txt` — pipeline 367-set, verifier OK, differs in 2 vertices
- `compute/R361_sprime.txt` — S' MIS construction, size 361, verifier OK
- `compute/verify_set.py` — pairwise checker
- logs: `orbit_search_wide.txt`, `three_out_log.txt`, `fold_near.txt`, `linear_probe.txt`, `local_search_log.txt`, `fewflip_sat_log.txt`, `minconflicts_cage.txt`, `cegar_product_log.txt`

## 6. What is proved vs still open

The 367-set is independent. $\alpha(C_7^{\boxtimes 5})\ge 367$ is old. This search did not find 368 and did not prove 367 is maximum. Lovász still gives $\alpha\le 401$. $\Theta(C_7)$ is not claimed from this folder.

# Attack log — C7 fifth power

## 2026-08-27 — q4, new shapes, Hamming 13 finished

Replay: `python3 compute/verify_set.py compute/R367.txt --min-size 367` → OK. Opened Polak–Schrijver arXiv:1808.07438v2 (Table 1 still $367$–$401$), Itty et al. 2607.21517v2 (fifth-power record still 367), Gao 2607.27869 (“it remains the largest currently known such set”), Buys–Polak–Zuiddam 2607.29681 (profile $(367,8,367,322)$). No 368 in those papers.

q3 closed the $8$-coset leftover. This pass hunted shapes that are not an $8$-coset pack, not a missing letter, and not Hamming $11$ from the seed.

**Hamming $13$ is finished.** q3 already killed $5$- and $6$-blocker adds (`best_mis=4`). Case C: every $4$-blocker plus two extra removals, $199{,}671{,}417$ pairs, `max_freed=14`, no $\alpha\ge 7$. Leftover SAT on the $1767$ vertices with $\le 3$ blockers ($153967$ clauses): Cadical UNSAT in $548$s. Combined with q1's odd ball through $9$ and q2's Hamming $11$, the odd Hamming ball through $13$ around this seed is empty. Logs: `compute/q4/hamming13_four_log.txt`, `hamming13_sat_log.txt`.

**$1$-dimensional good codes.** $(7^5-1)/6=2801$ subspaces, $2680$ good, $1156$ unique connection sets on $\mathbb F_7^4$. Degrees $188$–$242$. Hoffman never dropped below $53$ (best float $366.01$). Random greedy plus a short improve reached $43$ cosets ($301$ vertices); a harder ejection on five generators reached $46$ ($322$). Those packs had empty original-graph residual. No $371$-set. Cadical on a $53$-pack is unfinished (residue). `compute/q4/onedim_log.txt`, `grow_1dim_log.txt`.

**Cyclic-coordinate $5$-orbits.** $3360$ orbits, $3262$ internally independent. Greedy $\le 52$ orbits ($260$) or $53$ plus $\{00000,22222,44444\}$ ($268$). Cadical for $74$ orbits ($370$) is unfinished (residue). `compute/q4/cyclic_log.txt`.

**Negation pairs.** $8282$ internally independent pairs $\{v,-v\}$. Cadical for $184$ pairs ($368$) is unfinished (residue).

**Hamming $15$ high-blocker.** $2842$ vertices with $7$ blockers have freed $\alpha\le 4$; $1{,}406{,}817$ extensions of a $6$-blocker by one extra have freed $\alpha\le 5$. Residue: add only $\le 5$-blocker vertices. `compute/q4/hamming15_log.txt`.

**Ejection from $343$.** $80$ random good $3$-dimensional codes, $25000$ delete-and-repack steps each, `best=343`. The linear sets did not move. Residue. From-scratch GRASP, $40$ restarts: best $297$. Wider fold grid recovered $361$ by greedy residual (the published $367$ needs the exact $40$-set). Mixing the published $367$-set with the reconstructed pipeline set (symmetric difference $4$) has independence number $367$.

No $368$-set. No $\Theta(C_7)$ claim. $367^{1/5}\approx 3.25787<3.258805$. This is not a dent.

## 2026-08-27 — q3, 8-coset leftover finished

Replay: `python3 compute/verify_set.py compute/R367.txt --min-size 367` → OK. Opened Polak–Schrijver arXiv:1808.07438 (Table 1 still $367$–$401$), Itty et al. 2607.21517v2 (fifth-power record still 367; v2 only adds a $C_{15}$ capacity bound), Gao 2607.27869 (“it remains the largest currently known such set” in the fifth power), Buys–Polak–Zuiddam 2607.29681 (profile $(367,8,367,322)$). No 368 in those papers.

q2 left $1280$ quotient graphs after a node-capped search. Those were not $1280$ distinct problems. The $97240$ good $2$-dimensional codes collapse to $9584$ unique connection sets on $\mathbb F_7^3$ (degrees $122$–$228$). A Hoffman bound on the Cayley eigenvalues never dropped below $8$ (best float $33.12$). A multi-start clique cover killed $359$ graphs. An exact $8$-set search with clique-cover pruning and a $2\cdot 10^6$ node cap finished the other $9225$: `yes=0 leftover=0`. Every $7$-pack still has empty residual in the original graph (q2). No $392$-set of this shape.

Python replay of the RREF count matches $140050$ subspaces and $97240$ good codes. Cadical on a deterministic sample of $159$ unique graphs is UNSAT. The leftover file is empty, so the SAT queue is empty.

Hamming $13$ (6-out/7-in) around the published $367$-set, high-blocker split: $3897$ vertices with $6$ blockers have freed $\alpha\le 4$; $1{,}343{,}744$ extensions of a $5$-blocker vertex by one extra removal have freed $\alpha\le 4$. Residue: adding only $\le 4$-blocker vertices (Cadical on $4806$ candidates, $697012$ clauses, not finished).

No $368$-set. No $\Theta(C_7)$ claim. $367^{1/5}\approx 3.25787<3.258805$. This is not a dent.

## 2026-08-27 — q2 start, 4-support finished

Replay: `python3 compute/verify_set.py compute/R367.txt --min-size 367` → OK. Opened Polak–Schrijver arXiv:1808.07438 (Table 1 still $367$–$401$), Itty et al. 2607.21517, Gao 2607.27869 (“367 remains the largest currently known” in the fifth power), Buys–Polak–Zuiddam 2607.29681 (profile $(367,8,367,322)$). No 368 in those papers.

q1 left 4-support as a local-search residue (best grown $309$). That shape is impossible, and so are 5- and 6-support.

An adjacent pair of letters in one coordinate induces $K_2\boxtimes C_7^{\boxtimes 4}$. The two fibers project to a single independent set in $C_7^{\boxtimes 4}$, so they contribute at most $\alpha(C_7^{\boxtimes 4})\le 115$ (Baumert via Polak–Schrijver Table 1), not $230$. Every $k$-subset of $C_7$ with $k\le 6$ has matching number large enough that
$$
\nu\cdot 115+(k-2\nu)\cdot 115\le 345<368.
$$
All $126$ such subsets were enumerated (`compute/q2/bound_support.py`). Toy checks: $\alpha(K_2\boxtimes C_7)=3$, $\alpha(C_7^{\boxtimes 2})=10=\alpha(K_2\boxtimes C_7^{\boxtimes 2})$. The published $367$-set is $7$-surjective on every coordinate; its $35$ adjacent pair-fibers have size $100$–$107$ and project to independent $4$-tuples.

A $368$-set uses all seven letters in every coordinate.

Hamming $11$ (5-out/6-in) around the published $367$-set is finished. Split on the added vertices' blocker counts:

- 3712 vertices with $5$ blockers: each determines the removal $5$-set. Freed graphs have size $\le 11$, $\alpha\le 3$.
- $1{,}103{,}157$ extensions of a $4$-blocker vertex by one extra removal: freed size $\le 11$, $\alpha\le 4$.
- Leftover: add only $\le 3$-blocker vertices. Cadical, $1767$ candidates, $153218$ clauses: UNSAT in $102$s.

No $368$-set at Hamming distance $11$ from this seed. Combined with q1's Hamming $\le 9$, the odd ball through $11$ is empty. Logs: `compute/q2/hamming11_log.txt`, `compute/q2/hamming11_sat_log.txt`.

Ejection sample: $16$ restarts, $250000$ one-outs, $16672$ four-outs (`best_gain=0`), $8336$ five-outs (`best_gain=1`, size stayed $367$). Residue. `compute/q2/ejection_log.txt`.

Exact $8$-coset census of every $2$-dimensional subspace of $\mathbb F_7^5$: $140050$ subspaces (Gaussian $\binom{5}{2}_7$), $97240$ good ($V\cap\{-1,0,1\}^5=\{0\}$). Greedy and the capped exact search never found $8$ independent cosets. Every materialised $7$-pack had empty residual in the original graph (total $343$). First pass left $7040$ graphs at the node cap; a second Cayley search proved $5760$ of those have $\alpha<8$ and left $1280$ unknown. Residue, not a proof that no $8$-coset pack exists. No $392$-set. Logs: `compute/q2/coset_exact_log.txt`, `compute/q2/coset_unknown_c_log.txt`.

No $368$-set. No $\Theta(C_7)$ claim. $367^{1/5}\approx 3.25787<3.258805$.

## 2026-08-23 — replay

- Checkout `grok/c7-shannon`. Replayed `python3 compute/verify_set.py compute/R367.txt --min-size 367` → `size=367 unique=367`, `OK: independent in C7^{box5}`. Same verifier on `R_reconstructed.txt` (367) and `R361_sprime.txt` (361) also OK. This is the Polak–Schrijver record, not a dent.

## 2026-08-23 — six shapes for a 368-set (q1)

Work backwards from the shape, not from another 3-out census of the same seed. Baumert–McEliece–Rodemich–Rumsey–Stanley–Taylor give $\alpha(C_7^{\boxtimes 4})\le 115$ (their lemma $\alpha(C_n^d)\le \alpha(C_n^{d-1})n/2$). Polak–Schrijver Table 1 already records that 108–115 interval.

The published 367-set meets every letter in every coordinate, with fiber sizes 50–55. It differs from the reconstructed pipeline set in two vertices (`34035`,`64340` versus `24635`,`64246`), which are two of Gao's eight private pairs. The eight single-blocker vertices of the 367-set are exactly the eight private neighbours $q_j$.

1. **Three mutually non-adjacent slices.** Support in one coordinate on a 3-set of circular distance $\ge 2$ (e.g. $\{0,2,4\}$). The three fibers do not interact, so the size is at most $3\alpha(C_7^{\boxtimes 4})\le 345<368$. This shape is impossible. Every 368-set uses at least four letters in every coordinate.

2. **Four-letter support.** Average fiber 92, each $\le 115$. A 4-subset of $C_7$ always contains an edge; the split $\{0,1,3,5\}$ has a single adjacent pair and two free fibers.

3. **Punctured isolate core.** Polak–Schrijver keep $|M|=327$ isolates of the folded 382-orbit and add $\alpha=40$ from a 71-vertex residual. Deleting $k$ isolates and re-solving the *whole* residual (not a 3-out of the finished 367-set) aims at $327-k+\alpha(\text{new residual})\ge 368$. The S' MIS extreme ($357+4=361$) already showed that eating conflict vertices spends the leftover; this shape is the intermediate punctures.

4. **Eight cosets of a good 2-dimensional $\mathbb F_7$-code.** A 2-dimensional $V$ with $V\cap\{-1,0,1\}^5=\{0\}$ has 49-point cosets. Eight independent points of the 343-vertex quotient give 392 vertices. Seven cosets are only 343.

5. **A 5-dimensional fiber of a published higher-power set.** Itty–Rosin–Carstensen–Reichman $\alpha(C_7^{\boxtimes 6})\ge 1120$: after dropping one coordinate, the largest 5-fiber has size 165 (replayed from their `CC_6_7_1120.txt`, 1120 unique, independent). Their 10th-power gadget $I=(B\times B)\cup A_H\cup A_V$ of size 134753 has largest 5-fiber 367 (left or right), never 368. Those two certificates do not hide a 368-set in a fiber.

6. **A 367-set on the private-pair / translate plateau, plus one vertex.** Few-flip SAT only killed odd Hamming distance $\le 9$ around one seed. The even 1-out-1-in moves are the eight private-pair swaps; 108 of the 256 subsets remain independent 367-sets, including the reconstructed list. None of those 108 has a 1-out-2-in with newly-free set of size $\le 16$. Separately, the union $A\cup(A+v)$ is bipartite aside from the intersection. Among all 16806 nonzero translations, 8422 are disjoint from $A$; none has an isolated vertex in the bipartite conflict graph, so there is no cheap "$A$ plus one point of $A+v$". An imperfect maximum matching would still give 368; that is a C check, not the old 3-out SAT.

## 2026-08-23 — q1 results, no 368

Worked the six shapes backwards. No independent set of size 368. Timeouts and samples are residue, not a lower bound. The 3-support obstruction and the two-translate matching census are complete for those shapes.

1. **3-support.** Impossible: $3\cdot 115=345<368$. Recorded.

2. **4-support.** `search_4support.py`: every 4-subset of letters, slice the 367-set and grow. Best grown size 309 on $\{0,2,4,5\}$. Greedy fibers of $\{3,5\}$ plus a $\{0,1\}$-slice: $81+81+81=243$. Not a 368-set. Residue: not an exact $\alpha$ on the 9604-vertex induced subgraphs.

3. **Punctured isolate core.** `search_core_puncture.py`. $k=0$ recovers $327+40=367$. All 327 single punctures: residual 72 or 73, $\alpha=41$, total 367. Deleting one isolate frees exactly one extra leftover vertex. $k=2$ was stopped after 19 trials (residue). Log: `compute/q1/core_puncture_log.txt`.

4. **Eight cosets.** First C quotient encoding was wrong (claimed 13 cosets, $13\cdot 49=637>401$, impossible). Replaced by neighbourhood-true coset ids. C enumeration of RREF generators: $\ge 25000$ good codes, greedy $\le 7$ (total 343). Verified Python sample of 120 random good 2-dimensional codes: best 7, leftover of every 7-pack empty, so those packs are maximal in the quotient. Not a proof that no 8-coset pack exists. Residue. Log: `compute/q1/coset_sample_log.txt`.

5. **Higher-power fibers.** Replayed. Itty 1120-set in dimension 6 is independent; max 5-fiber 165. Itty/Gao 10th-power gadget from R367: max 5-fiber 367. Those two certificates do not contain a 368-set as a fiber. `compute/q1/profile_log.txt`.

6. **Plateau / translates / ejection.** `search_translates.c`: all 16806 nonzero $v$, $8422$ disjoint and $8384$ intersecting, maximum matching always perfect, $\alpha(A\cup(A+v))=367$ for every $v$. No 368-set of this shape. `search_plateau.c`: 108 private-pair 367-sets, $7253388$ two-out packs, `best_gain=0`. `search_ejection.c`: 6 restarts, 250000 one-out steps each, 7500 sampled four-outs, `global_best=367`, `four_out_best_gain=0`. The translate census is complete for that shape; ejection is a sample (residue).

No $\Theta(C_7)$ claim. $367^{1/5}\approx 3.25787<3.258805$. A 368-set is still the finite bound that would move $\alpha(C_7^{\boxtimes 5})$.

## 2026-08-16

- Folder created. Grok 4.6 cloud agent launched.

## 2026-08-16 — reconstruction

- Read Polak–Schrijver IPL 2019 / arXiv:1808.07438. The 367-set is an adapted Reed–Solomon orbit in $C_{108,382}^{\boxtimes 5}$, not a linear $\mathbb F_7$-code (those max out at $7^3=343$).
- July 2026 papers (Itty et al. 2607.21517, Gao 2607.27869, Buys–Polak–Zuiddam 2607.29681) improve $\Theta(C_7)$ in dimensions 10 and 200. All three still treat 367 as the fifth-power record.
- Copied the published 367 words from [Itty `c7/R367.txt`](https://raw.githubusercontent.com/nathanielitty/lower-bounds-for-shannon-capacity/main/c7/R367.txt) into `compute/R367.txt`.
- Verifier `python compute/verify_set.py compute/R367.txt --min-size 367` → OK, 367 unique, independent.
- `reconstruct_polak.py` replays §3: fold unique 382, $|M|=327$, residual 71 verts / 85 edges, $\alpha=40$, $|R|=367$. Matches the paper. Reconstructed set differs from the published list in 2 vertices (two different 40-sets in the same residual). Both verify.

## 2026-08-16 — searches, no 368

- **Direct geometric orbits.** `search_orbits.py` over $n=300..600$: no pair with $k(n,5,q)\ge 2n/7$. Closest misses: $317/90\approx 3.522$ ($q=31$, one short of the homomorphism) and the published $382/108\approx 3.537$. Random non-geometric generators $t\cdot(1,a,b,c,d)$ for $n=368..400$, 80 samples each: no hit.
- **S' MIS instead of isolates.** Conflict component of the folded 382-set has 55 verts, 35 edges, $\alpha=30$. Isolates + that MIS gives $M=357$, residual 4, total **361** (`R361_sprime.txt`, verifies). Greedy on $S'$ shrinks the leftover that was worth 40.
- **Local swaps from the 367-set.** Free vertices: 0 (maximal). Exhaustive 1-out: none. Exhaustive 2-out: 67161 trials, none. Exhaustive 3-out: 8171255 trials, `best_gain=0` in 419s. Sampled 4-out (3000) and two anneal restarts: stayed at 367.
- **Linear 3-dim codes.** 30 random good $\mathbb F_7^3$ subspaces: every residual empty, total stuck at 343. $V+\{-1,0,1\}^5=(\mathbb Z/7\mathbb Z)^5$.
- **Fold-and-repair on near-miss orbits** (317, 382, 309, 303, 301, 339, 367, 362). Best is the published shift on $n=382$, $q=7$, den=109: 327+40=367. Other 382-translations scored 357–360. Smaller $n$ collapsed to $M\sim 30$ and totals $\sim 250$.
- **Shifts.** Published $(40,123,40,123,40)$ recovered as the best completed score. Broader translation grid not finished (exact MIS on 70-vertex leftovers is slow). No 368 in the completed prefix.

## 2026-08-16 — steal from W(2,7)

- Sibling finished with no dent (best verified colouring length 3703). Methods stolen: `CardEnc.atmost` only; few-flip SAT around the published seed; treat a one-violation min-conflicts stall as a cage; CEGAR on a product template and stop if leftovers plateau.
- Scripts: `search_fewflip_sat.py`, `search_minconflicts_cage.py`, `search_cegar_product.py`. A 367-set is not a dent. No $\Theta(C_7)$ claim.
- **Few-flip SAT.** Cadical195 + `CardEnc.atmost` (kmtotalizer; at-least via negated at-most). Free vertices 0. Hamming $\le 9$ is UNSAT, including 4-out/5-in (4806 candidates, 67s). Hamming 11 with 5 removals timed out. Local cage, not a bound.
- **Min-conflicts cage.** 367 plus one extra, 8 trials: stalled at 787–846 adjacent pairs. Not one leftover; still a cage, not optimality.
- **Product CEGAR.** SAT built a 10-set in $C_7^{\boxtimes 2}$ and a 33-set in $C_7^{\boxtimes 3}$. Product has size 330 and empty residual. Incremental constraints have nothing to add; leftover count is already 0 and the size is 38 short. Stopped.

## Result

No independent set of size $\ge 368$. A 367-set is not a dent. No certificate that 367 is maximum: Lovász still allows 401; few-flip SAT only kills a Hamming ball of radius 9 around one seed. Do not claim a new $\Theta(C_7)$. $367^{1/5}\approx 3.25787 < 3.258805$.

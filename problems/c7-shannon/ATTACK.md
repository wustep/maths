# Attack log — C7 fifth power

## 2026-08-23 — replay

- Checkout `grok/c7-shannon`. Replayed `python3 compute/verify_set.py compute/R367.txt --min-size 367` → `size=367 unique=367`, `OK: independent in C7^{box5}`. Same verifier on `R_reconstructed.txt` (367) and `R361_sprime.txt` (361) also OK. This is the Polak–Schrijver record, not a dent.

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

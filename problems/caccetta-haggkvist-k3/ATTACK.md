# Attack log — Caccetta–Häggkvist for directed triangles

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Conjecture (Caccetta–Häggkvist 1978): every simple n-vertex digraph of minimum out-degree at least r has a directed cycle of length at most ⌈n/r⌉.
- First open case, and tonight's problem: whether δ⁺ ≥ n/3 forces a directed triangle.
- Tonight: a certified small-order obstruction, an improved numerical out-degree threshold with an independently checkable certificate, or a documented residue. Isolated random-graph statistics are not a dent.

### Published record (fetched tonight)

AIM workshop summary: Sullivan, *A Summary of Results and Problems Related to the Caccetta-Häggkvist Conjecture* (14 Apr 2006), local `compute/refs/sullivan-aim-caccetta.pdf`. Egres page timed out.

| claim | source | status |
| --- | --- | --- |
| r=2 | Caccetta–Häggkvist 1978 | theorem |
| r=3 | Hamidoune, JCTB 1987 | theorem |
| r=4,5 | Hoàng–Reed, Discrete Math. 1987 | theorem |
| r ≤ √(n/2) (precisely: n ≥ 2r²−3r+1) | Shen, Discrete Math. 2000 | theorem; finitely many exceptions per r |
| cycle length ≤ n/r + 73 | Shen, Graphs Combin. 2002 | theorem |
| Cayley / vertex-transitive | Hamidoune 1981 / 1987 | theorem |
| c ≤ (3−√5)/2 ≈ 0.3820 | Caccetta–Häggkvist 1978 | theorem |
| c ≤ (2√6−3)/5 ≈ 0.3798 | Bondy, Discrete Math. 1997 | theorem |
| c ≤ 3−√7 ≈ 0.3542 | Shen, JCTB 74 (1998) | theorem |
| c ≤ 0.3532 | Hamburger–Haxell–Kostochka, Electron. J. Combin. 2007 | theorem; uses Chudnovsky–Seymour–Sullivan |
| c ≤ 0.3465 | Hladký–Král'–Norin, Combinatorica 37 (2017); arXiv:0908.2791v4 | theorem; flag algebras on F₄ plus induction + CSS. Ancillary Maple `CH.mw` |
| c ≤ 0.3388 | de Joannis de Verclos–Sereni–Volec, March 2014 | **personal communication**, cited in HKN v4 and in Grzesik–Volec IMRN 2023 as [18]. Uses F₆. No paper, no public certificate |
| both δ⁺,δ⁻ ≥ 0.343545 n | Lichiardopol, Discrete Math. 2010 | theorem; two-sided, not the unrestricted out-degree problem |
| CH for three forbidden 4-vertex digraphs | Razborov, Combin. Probab. Comput. 2013? arXiv:math/0604317 | theorem; restricted class |

HKN (and every later citation that needs a published number, including Grzesik–Volec IMRN 2023 Theorem 2.2) still states **0.3465n** as the refereed unrestricted threshold. The 0.3388 figure is on the record as a personal communication only.

The cyclic construction (out-neighbours {1,…,⌊(n−1)/3⌋} on ℤ/n) is C₃-free and meets the conjectured threshold: so the exact finite statement is

> every n-vertex oriented graph with δ⁺ ≥ ⌈n/3⌉ has a directed triangle.

HKN implies this whenever ⌈n/3⌉ ≥ 0.3465 n. Combined with Hoàng–Reed (r≤5) the first n where the exact statement is not implied is **n=18, δ⁺=6** (0.3465·18 = 6.237). The 0.3388 communication still has 0.3388·18 = 6.098 > 6, so n=18 is open even if one grants that number. Same for n=21,24,27,…

Hamidoune already kills every Cayley counterexample, so a circulant search cannot produce an obstruction.

### Plan

1. Fetch HKN, the AIM summary, Grzesik–Volec, Razborov; replay HKN's F₄ certificate independently from the published matrices and from a from-scratch flag count.
2. Re-optimise HKN's linear combination on the same F₄ inequalities; a verified c < 0.3465 is a dent against Combinatorica. Beating 0.3388 would need F₆ or a new inequality and is not assumed.
3. SAT-certify the exact statement at the first open order n=18 (and as far as the solver reaches). A DRAT/UNSAT proof, or a C₃-free 6-outregular oriented graph, is the product. The latter would disprove the conjecture; do not expect it.
4. If neither a better c nor a finished n=18 certificate appears, leave the residue. Do not call a partial search a bound.

Local PDFs and `CH.mw`: `compute/refs/`.

## 2026-08-17 — HKN certificate shape

HKN Theorem 3.3: every homomorphism Ψ of the flag algebra of triangle-free oriented graphs satisfies δα(Ψ) < 0.3465. Proof reduces to emptiness of a set R(c) ⊂ ℝ³² of 4-vertex type densities r = (Ψ(H₀),…,Ψ(H₃₁)) obeying

- r ≥ 0, ‖r‖₁ = 1
- AC(r) ≽ 0 (8×8 Cauchy–Schwarz on β-flags)
- b(BR − c AR)rᵀ ≥ 0 for all b (out-regularity)
- IndT(r) ≥ 0, IndV(r) ≥ 0 (order-3 induction, Shen-style)
- Fork(r) ≥ 0 (CSS + Jensen on forks)

They exhibit four vectors aᵢ ∈ ℝ⁸, one b ∈ ℝ¹⁴, and scalars cT, cV, d such that the linear form F(c,r) is a nonnegative combination of those inequalities, F is nonincreasing in c, and F(0.3465, r) has every coordinate strictly negative (worst −1.24639). Hence R(0.3465)=∅.

The aᵢ are two-decimal; the claimed F coefficients are called “exact”. Independent replay is `compute/hkn_replay.py`.

## 2026-08-17 — matrices rebuilt from scratch

`flags4.py` enumerates all 549 labeled C₃-free oriented graphs on 4 vertices, matches HKN’s 32 types H₀…H₃₁ (pairwise non-isomorphic), and rebuilds AC. **Every entry of Table 1 matches exactly**, no scale.

AR and BR match Table 2 after dividing the labeled count by 2 (HKN’s extras in a λ-flag are unordered). IndT and Fork match (4.14) and the fork identity exactly (`ind_fork.py`). IndV is twice (4.15) before the published factor 12 (type V has an extra automorphism). So the linear pieces of the HKN certificate are independently checked.

Plugging the *printed two-decimal* aᵢ into F does **not** reproduce (4.22). The display rounding of aᵢ is fatal; (4.22) was computed from higher-precision vectors that are not in the paper (the Maple worksheet stores them as encoded floats). We do not trust (4.22) as a certificate.

## 2026-08-17 — F₄ threshold of this system

`optimize_bound.py` (HiGHS LP on the linear multipliers, Q = Σ a aᵀ plus random PSD) and `sdp_bound.py` (CVXPY/SCS, feasibility Fₖ ≤ −1) agree: the HKN F₄ inequality system becomes empty at

> c⋆ ≈ 0.346439.

HKN published 0.3465, a four-decimal rounding. The same system, with an explicit Q ≽ 0 and (b, cT, cV, d), certifies **c = 0.34645** with worst coordinate F = −0.12343 (`certs/f4_certificate.json`). `verify_certificate.py` replays it against the rebuilt matrices.

This is a fifth-decimal tightening of Combinatorica, not a new method. It does **not** beat the 0.3388 personal communication. An F₅ lift (317 types, 14×14 λ-flag SOS plus the pulled-back F₄ block) did not improve the threshold (`optimize_f5.py`).

Linear-only R′(c) (no SOS) is nonempty down through 1/3 + ε and empty only around 0.38 — Bondy/Shen territory. The SOS is doing the work.

## 2026-08-17 — SAT encoding, two bugs, then a census

First CNF used a broken Sinz cardinality encoding. Kissat returned SAT for n=6, d=2; the model had min out-degree 1 and 2-cycles. Discarded. Replaced by binomial at-least / at-most (no auxiliaries).

`verify_model.py` reads only `v`-lines (the first version parsed numbers out of the kissat banner). After the fix:

| n | d = ⌊(n−1)/3⌋ cyclic | d = ⌈n/3⌉ conjecture |
| ---: | --- | --- |
| 5 | SAT C₅ | UNSAT |
| 6 | SAT | UNSAT (CH r=2) |
| 7–8 | SAT circulant | UNSAT at +1 |
| 9 | SAT | UNSAT |
| 10 | SAT | UNSAT |

All SAT models checked: out-regular, no 2-cycle, no C₃.

Without lex SB, n=12 d=4 (Hoàng–Reed) is already too hard: 180s, 1.8M conflicts, UNKNOWN. With lex order on out-neighbourhoods of N⁺(0) and of the complement:

- n=12 d=4: UNSAT, 2993 conflicts, 0.07s. DRAT verified (`drat-trim`).
- n=15 d=5: UNSAT, 137486 conflicts, 6.0s. DRAT verified.
- n=16 d=6: UNSAT, 35382 conflicts, 3.5s. DRAT verified. (HKN already implies this: 0.3465·16 < 6.)
- n=17 d=6: UNSAT, 654582 conflicts, 63s. DRAT verified. (HKN: 0.3465·17 < 6.)

n=18 d=6 is the first order not implied by Hoàng–Reed or HKN (0.3465·18 = 6.237 > 6; even 0.3388·18 = 6.098 > 6). Kissat still UNKNOWN at 20 min / 10.3M conflicts (`certs/n18_residue.json`).

Local search from the circulant plus one extra out-edge per vertex never produced a C₃-free (r+1)-regular graph on n≤24 (`hunt_plus_one.py`). Isolated, as required.

## 2026-08-17 — what would be a dent vs what we have

- **Numerical:** 0.34645 < 0.3465, independently checkable F₄ certificate. Tiny. Did not beat 0.3388.
- **Small-order:** DRAT-verified exact CH-triangle at n=12,15,16 (and n=17 pending proof). n=16 is the first n with ⌈n/3⌉=6. n=18 is the first n where this is not already a theorem. Residue if the n=18 run dies.

## 2026-08-27 — q1, first open order

Continue the 17 August campaign. Published unrestricted threshold is still HKN Combinatorica 0.3465: fetched arXiv:0908.2791v4 tonight; the abstract and Theorem 1.2 still state 0.3465n. Grzesik–Volec arXiv:2102.12830v2 (updated 2024-01-18) still quotes that number as the published out-degree bound and leaves 0.3388 as a personal communication. Cheng–Keevash arXiv:2402.16776 (2024) cites HKN 0.3465 as the triangle-case input. ProofAtlas's 2 August 2026 check still lists 0.3465 as the peer-reviewed unrestricted threshold. Do not treat 0.3388 as published.

The stored F₄ certificate at c=0.34645 still replays (worst F=−0.12343, min eig 9.5·10⁻⁹). The same (Q,b) ray stays strictly negative through c=0.34644447 (worst F=−0.0225) and goes positive at 0.34644. So this system does not give a clean fifth-decimal step below 0.34645; 0.34645 remains the frozen number. F₅ already failed to move the threshold. Beating 0.34645 needs a new inequality or F₆.

The leftover that counts is the exact statement at n=18, δ⁺=6. Code for this run is `compute/q1/`. Two changes to the SAT encoding:

1. Sinz sequential counters replace the binomial at-most/at-least. The 17 August CNF was `p cnf 819 465269` mostly from C(17,7) per vertex.
2. Split on k=|N⁻(0)| and fix N⁻(0)={7,…,6+k} by relabelling. Each cube is a separate instance. k=11 is empty by counting: each v∈N⁺(0) would need 6 out-neighbours from 5 legal candidates.

A DRAT/UNSAT on every cube, or a verified C₃-free 6-outregular model, is the product. Incomplete SAT is residue.

### 2026-08-27 — cubes

Sequential-counter encoding recovers the 17 August census. DRAT-verified tonight with the new encoder: n=6 d=2, n=9 d=3, n=12 d=4, n=15 d=5, n=16 d=6, n=17 d=6 (18s; was 63s). Cube split on n=9 d=3 is all UNSAT; on n=9 d=2 some k are SAT with checked models. So the in-neighbourhood cut is not vacuously empty.

n=18 d=6 cubes, kissat 4.0.4:

| k=|N⁻(0)| | status | time | DRAT |
| ---: | --- | ---: | --- |
| 11 | UNSAT | 0.002s | VERIFIED, 8kB |
| 10 | UNSAT | 0.002s | VERIFIED, 12kB |
| 9 | UNSAT | 0.004s | VERIFIED, 24kB |
| 8 | UNSAT | 0.003s | VERIFIED |
| 7 | UNSAT | 0.012s | VERIFIED, 44kB |
| 6 | UNSAT | 0.03s | VERIFIED, 39kB |
| 5 | UNSAT | 1.1s | VERIFIED, 2.6MB |
| 4 | UNSAT | 6s | (proof running) |
| 3 | UNSAT | 24s | (proof running) |
| 2 | UNSAT | 115s | VERIFIED, then dropped (245MB) |
| 1 | UNKNOWN | 180s with proof log | leftover |
| 0 | UNKNOWN | 180s with proof log | leftover |

k=0 and k=1 reran without proof logging (600s): **k=1 UNSAT in 596s**. Regenerated with proof: kissat 587s, DRAT **VERIFIED**, 1.207 GB (`certs/keep/ch-18-6-k1-proof.json`, sha256 `73441d6e…`). The proof is too large to store; replay is `python3 solve.py --n 18 --d 6 --indeg0 1 --time 900 --proof`. k=0 still UNKNOWN at 600s.

Second split t=|N⁺(1) ∩ U|:

- k=0, t=1..5: UNSAT, DRAT stored and replayed
- k=0, t=6: UNKNOWN at 900s (`--stable`)
- k=1, t=1..5: UNSAT, DRAT stored and replayed
- k=1, t=6: implied by the whole-k=1 DRAT

Third split of (k=0,t=6) on s=|N⁺(2) ∩ (N⁺(1) ∩ U)| timed out at 180s for s=0,1,2,3. That leftover is unused.

**Pigeonhole.** A 6-outregular oriented graph on 18 vertices has 108 arcs, so some vertex has in-degree ≥ 6. Relabel that vertex as 0, its out-neighbours as 1..6, its in-neighbours as 7..6+k, and sort each block to meet the lex cut. The exact statement at n=18 therefore reduces to cubes k=6..11.

Those six cubes are UNSAT with stored, replayed DRATs (`certs/keep/ch-18-6-k{6..11}.{cnf,drat}`). So every 18-vertex oriented graph with δ⁺ ≥ 6 has a directed triangle.

This is a dent against the finite hole, not against HKN 0.3465 (that number already misses n=18). Did not beat 0.34645. Did not treat 0.3388 as published. The k=0 search is leftover bookkeeping, not a bound.

## 2026-08-27 — q2, next exact holes

Continue from the n=18 pigeonhole. Code is `compute/q2/`. Published unrestricted threshold is still HKN Combinatorica 0.3465: fetched arXiv:0908.2791v4 tonight (abstract and Theorem 1.2 still 0.3465n; no later version). Grzesik–Volec arXiv:2102.12830v2 still does not replace the unrestricted triangle number. Cheng–Keevash arXiv:2402.16776v4 (21 Aug 2024) quotes HKN 0.3465 as the triangle-case input and proves a path-length statement, not a new c. No arXiv hit after 2024 states a published unrestricted c < 0.3465 with a public certificate. Do not treat 0.3388 as published. The stored F₄ certificate at 0.34645 is not to be moved unless a new inequality appears.

After n=18, the first remaining exact order is n=21, δ⁺=7 (0.3465·21 = 7.2765 > 7; even 0.3388·21 = 7.1148 > 7). Then n=24, and a few near-threshold orders such as n=26 (0.3465·26 = 9.009 > 9). A 7-outregular oriented graph on 21 vertices has 147 arcs, so some in-degree is at least 7. Same encoder as q1: cubes k=|N⁻(0)|. Counting on N⁺(0) empties k=13. The statement reduces to k=7..12.

A DRAT/UNSAT on every needed cube, or a verified C₃-free 7-outregular model, is the product. Incomplete SAT is residue. Isolated random-graph statistics are not a bound.

### 2026-08-27 — cubes through n=36

Same encoder as q1. High-k cubes first, kissat 4.0.4, DRAT checked against a CNF regenerated from `encode.py` (not against leftover scratch files).

Soundness: n=21 d=6 k=6 is SAT in 0.15s with a checked C₃-free 6-outregular model. n=24 d=7 k=7 is SAT in 7s, same check. So the encoder is not vacuously UNSAT at these orders.

Every needed cube k≥d at the remaining holes through n=36 is UNSAT. Each proof is tens to a few hundred kilobytes and finishes in well under a second:

| n | d | cubes | worst time | DRAT |
| ---: | ---: | --- | ---: | --- |
| 21 | 7 | k=7..12 | 0.04s | VERIFIED, stored |
| 24 | 8 | k=8..14 | 0.04s | VERIFIED, stored |
| 26 | 9 | k=9..15 | 0.06s | VERIFIED, stored |
| 27 | 9 | k=9..16 | 0.07s | VERIFIED, stored |
| 29 | 10 | k=10..17 | 0.05s | VERIFIED, stored |
| 30 | 10 | k=10..18 | 0.07s | VERIFIED, stored |
| 32 | 11 | k=11..19 | 0.07s | VERIFIED, stored |
| 33 | 11 | k=11..20 | 0.06s | VERIFIED, stored |
| 35 | 12 | k=12..21 | 0.07s | VERIFIED, stored |
| 36 | 12 | k=12..22 | 0.16s | VERIFIED, stored |

Independent replay: `python3 verify_keep.py` (95 cubes, 0 failures).

So every oriented graph on one of those n with δ⁺ ≥ ⌈n/3⌉ has a directed triangle. This is a dent against those finite holes, not against HKN 0.3465. Did not beat 0.34645. Did not treat 0.3388 as published.

The first remaining hole is n=38, δ⁺=13 (0.3465·38 = 13.167 > 13). Then 39, 41, 42, … . Those were not run.

## 2026-08-27 — q3, first leftover hole n=38

Continue from the q2 certificates through n=36. Code is `compute/q3/`. Published unrestricted threshold is still HKN Combinatorica 0.3465: fetched arXiv:0908.2791v4 tonight (abstract and Theorem 1.2 still 0.3465n; no later version). Grzesik–Volec arXiv:2102.12830v2 still does not replace the unrestricted triangle number. Cheng–Keevash arXiv:2402.16776v4 quotes HKN 0.3465 as the triangle-case input. Mezher–Daamouch arXiv:2405.17797 is a restricted-class second-neighbourhood note, not a new unrestricted c. No arXiv hit after 2024 states a published unrestricted c < 0.3465 with a public certificate. Do not treat 0.3388 as published. The stored F₄ certificate at 0.34645 is not to be moved unless a new inequality appears.

After n=36, the first remaining exact order is n=38, δ⁺=13 (0.3465·38 = 13.167 > 13; even 0.3388·38 = 12.8744 < 13, so granting the personal communication would already imply n=38 — we do not grant it). Then 39, 41, 42, 44, 45, … . A 13-outregular oriented graph on 38 vertices has 494 arcs, so some in-degree is at least 13. Same encoder as q1/q2: cubes k=|N⁻(0)|. Counting on N⁺(0) empties k=24. The statement reduces to k=13..23.

Replay q2 first: `cd compute/q2 && ./run_all.sh`. A DRAT/UNSAT on every needed cube at n=38 (and as many later holes as finish), or a verified C₃-free 13-outregular model, is the product. Incomplete SAT is residue. Isolated random-graph statistics are not a bound. A new F₄/F₆ certificate with some c < 0.34645 would be a numerical dent; the same (Q,b) ray does not give one.

### 2026-08-27 — cubes through n=72

q2 replay first: F₄ still 0.34645 (worst F=−0.12343); 95 stored pigeonhole DRATs, 0 failures.

Same encoder as q1/q2. High-k cubes first, kissat 4.0.4, DRAT checked against a CNF regenerated from `encode.py`.

Soundness: n=21 d=6 k=6 is SAT in 0.15s with a checked C₃-free 6-outregular model. The n=38 circulant (d=12) is C₃-free and 12-outregular; after placing N⁺(0) and N⁻(0), every arc-variable clause of both the non-SB and the lex-SB cube is satisfied (`certs/keep/soundness_n38_d12.json`). Kissat searching for that SAT model timed out at 60s; the explicit circulant is the check. The encoder is not vacuously UNSAT at these orders.

Every needed cube k≥d at the remaining holes through n=72 is UNSAT. Each proof is tens of milliseconds to a couple of seconds:

| n | d | cubes | worst time | DRAT |
| ---: | ---: | --- | ---: | --- |
| 38 | 13 | k=13..23 | 0.12s | VERIFIED, stored |
| 39 | 13 | k=13..24 | 0.15s | VERIFIED, stored |
| 41 | 14 | k=14..25 | 0.13s | VERIFIED, stored |
| 42 | 14 | k=14..26 | 0.15s | VERIFIED, stored |
| 44–72 | ⌈n/3⌉ | every k≥d not empty by count | ≤1.9s | VERIFIED, stored |

Independent replay: `python3 verify_keep.py` (534 cubes). Orders closed tonight: 38, 39, 41, 42, 44, 45, 47, 48, 50–72. The n≡1 (mod 3) values 40, 43, 46, 49 are already implied by HKN 0.3465 and were not cubes.

So every oriented graph on one of those n with δ⁺ ≥ ⌈n/3⌉ has a directed triangle. This is a dent against those finite holes, not against HKN 0.3465. Did not beat 0.34645.

A second F₄ Cauchy–Schwarz block on the order-2 non-edge type was tried (`sos_nonedge.py`). The old c=0.34645 still certifies (t=−0.77); at c=0.346 the best t is +73. The extra SOS did not move the threshold. F₄ residue, not a numerical dent.

The first remaining hole is n=73, δ⁺=25. The conjecture 1/3 is open. Did not treat 0.3388 as published.

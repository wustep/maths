# Walkthrough — Caccetta–Häggkvist for directed triangles

## 0. What was actually missing

The refereed unrestricted threshold is Hladký–Král'–Norin 0.3465 (*Combinatorica* 2017): every n-vertex oriented graph with δ⁺ ≥ 0.3465 n has a directed triangle. The cyclic construction meets the conjectured 1/3, so the exact finite statement is

> δ⁺ ≥ ⌈n/3⌉ forces a C₃.

Hoàng–Reed (r ≤ 5) plus HKN leave a first open order: **n=18, δ⁺=6**, because 0.3465·18 = 6.237 > 6. (The 0.3388 figure cited from 2014 is a personal communication, F₆, no public certificate; even that number still has 0.3388·18 > 6.)

A new bound tonight is either a checkable certificate with some c < 0.3465, or a DRAT-verified proof that no 6-outregular C₃-free oriented graph on 18 vertices exists. Isolated random-graph statistics are not a new bound.

## 1. Named false starts

**Treat 0.3388 as the published record.** Grzesik–Volec (IMRN 2023) cite it as [18] “personal communication”. HKN v4 (arXiv, 2016) says de Joannis de Verclos–Sereni–Volec pushed the bound to 0.3388 in March 2014 using F₆ “and several additional bounds”. There is no paper and no Maple/SDP file. The refereed number remains 0.3465. We compare against Combinatorica and *say* we did not beat 0.3388.

**Replay (4.22) from the printed aᵢ.** HKN exhibit four vectors with two decimal places and a 32-term expansion they call exact. Rebuilding AC, AR, BR, IndT, IndV, Fork from the 32 types (549 labeled C₃-free oriented graphs on 4 vertices) matches Tables 1–2 and (4.14)–(4.15) exactly. Feeding in the printed aᵢ does *not* match (4.22). The display rounding kills the combination. The Maple worksheet `CH.mw` stores the real aᵢ as encoded floats; we did not decode them. (4.22) is not a certificate we can check.

**Sinz cardinality, first CNF.** n=6, d=2 came back SAT in a millisecond. Caccetta–Häggkvist already proved r=2. The model had min out-degree 1, 2-cycles, and triangles. The sequential counter was attaching the wrong literals. Thrown away.

**Verifier that parsed the kissat banner.** Version strings and dates became “positive variables”. Fixed by reading only `v`-lines.

**F₅ SDP as a feasibility problem F ≤ −1.** 317 types, 14×14 λ-flag SOS. SCS reported infeasible at 0.3465, which is absurd: the F₄ certificate pulled back along the 4-vertex marginal is already a feasible F₅ ray. After adding the pulled-back 8×8 F₄ SOS block, SCS still could not find a strictly better c. Random PSD + LP on the same lift (`optimize_f5.py`) sat at the F₄ threshold. The 0.3388 communication used F₆ and extra bounds we do not have.

**n=12 without symmetry.** 144 variables, 8k clauses, Hoàng–Reed says UNSAT. Kissat burned 180s / 1.8M conflicts and returned UNKNOWN. The binomial encoding is correct and hopeless without a symmetry cut.

## 2. The useful failure

The HKN F₄ system, independently rebuilt, is a 32-dimensional Farkas problem: Q ≽ 0 on eight β-flags, 14 out-regularity rows, two order-3 induction forms, one CSS-fork form. Linear-only (no SOS) dies only around c ≈ 0.38. The SOS is what takes 0.38 down to 0.3465. An SDP on that exact system saturates at **0.346439**. HKN’s 0.3465 is a four-decimal rounding of this (or of a nearby) number. There is no more juice in F₄.

That is why n=18 is the finite handle. HKN does not imply δ⁺=6 forces a triangle on 18 vertices. A SAT proof there is not implied by any published threshold.

The n=12 UNKNOWN, next to the n=9 UNSAT in 0.01s, said the encoding was fine and the symmetry was missing. Lex order on out-neighbourhoods of N⁺(0) = {1,…,d} (and of the complement) collapsed n=12 to 2993 conflicts.

## 3. The click

Two small ones.

**The published 0.3465 is a rounding.** Once the matrices matched and the SDP sat at 0.346439, a certificate at 0.34645 was just “don’t round up”. `certs/f4_certificate.json`: Q ≽ 0 (min eigenvalue 9.5·10⁻⁹), worst F-coordinate −0.12343. Replayed against the rebuilt matrices.

**Lex SB turns Hoàng–Reed into a SAT proof.** With N⁺(0) fixed and out-neighbourhoods of 1 < 2 < ⋯ < d lex-ordered, kissat + `drat-trim` give independently checkable UNSAT proofs at the first two Hoàng–Reed orders and at the first HKN-only order:

| n | d | conflicts | time | DRAT |
| ---: | ---: | ---: | ---: | --- |
| 12 | 4 | 2993 | 0.07s | VERIFIED |
| 15 | 5 | 137486 | 5.96s | VERIFIED |
| 16 | 6 | 35382 | 3.46s | VERIFIED |
| 17 | 6 | 654582 | 63s | VERIFIED |

n=16 is the first n with ⌈n/3⌉ = 6. HKN already covers it (0.3465·16 < 6). n=18 is the first n it does not.

## 4. The argument, in the order it was found

1. Fetch Sullivan’s AIM summary, HKN arXiv:0908.2791v4 + `CH.mw`, Grzesik–Volec 2102.12830, Razborov math/0604317, Hamburger–Haxell–Kostochka. Record 0.3465 as refereed, 0.3388 as personal communication.
2. Rebuild the 32 types and the matrices. Match the paper. Fail to replay (4.22) from two-decimal aᵢ.
3. Re-optimise Q and the linear multipliers. The system dies at 0.346439. Freeze a certificate at 0.34645.
4. Try F₅. No improvement.
5. SAT with a broken cardinality encoding. Catch it on n=6 d=2.
6. Binomial encoding. Census n≤11 matches the cyclic construction (SAT) and the conjecture (UNSAT).
7. n=12 without SB does not finish. Add lex SB. n=12, 15, 16, 17 go UNSAT. DRAT-check the first three.
8. Start n=18 d=6, the first open order. Hunt-from-circulant never finds a 6-regular C₃-free graph on 18 vertices. n=17 DRAT-checked after the fact.

The F₄ certificate is checked as follows. The 8×8 slices Mₖ of AC, the 14×32 matrices AR, BR, and the linear forms IndT(c), IndV(c), Fork(c) are those of HKN, independently counted. For the stored Q, b, cT, cV, d and c = 0.34645,

    Fₖ = ⟨Q, Mₖ⟩ + b·(BR − c AR)ₖ + cT IndTₖ + cV IndVₖ + d Forkₖ

is negative for every k=0…31 (worst −0.12343 at H₀). Q has no negative eigenvalue. Hence no density vector r ≥ 0, ‖r‖₁=1 can lie in R(c), hence no homomorphism of the flag algebra of triangle-free oriented graphs has δα ≥ 0.34645.

## 5. Computer search

- F₄ matrices and type census: `certs/flags4.json`.
- F₄ certificate: `certs/f4_certificate.json`. Replay: `verify_certificate.py`.
- F₄ SDP log: `certs/sdp_bound.json` (saturation ≈ 0.346439).
- F₅ types (317) and lift: `certs/flags5.pkl`, `optimize_f5.json`. No better c.
- Small-n SAT: `certs/small_n_census.json`.
- DRAT-verified UNSAT: `certs/ch-{12-4,15-5,16-6,17-6}-sb.{cnf,drat}`.
- n=18 d=6: `certs/ch-18-6-sb.cnf`, `certs/n18_residue.json`. Kissat 4.0.4 still UNKNOWN at 20 min / 10.3M conflicts / 302 remaining variables. Incomplete search.
- Circulant-plus-one hunt: `certs/hunt_plus_one.json`. No C₃-free (r+1)-regular example on n≤24.

## 6. What is proved vs still open

**Proved tonight (checkable).**

- Every n-vertex oriented graph with δ⁺ ≥ 0.34645 n has a directed triangle. This is the HKN F₄ method with an independent matrix rebuild and a stored PSD certificate. It is 5·10⁻⁵ below the published 0.3465. It is not below 0.3388.
- Exact CH-triangle at n=12 (d=4), n=15 (d=5), n=16 (d=6), n=17 (d=6), with DRAT proofs. n=12 and n=15 recover Hoàng–Reed; n=16 and n=17 are implied by HKN.

**Still open (17 August).**

- The conjecture (c = 1/3).
- Any improvement of the 0.3388 personal communication.
- The exact statement at n=18, δ⁺=6 — the first order not implied by Hoàng–Reed or HKN — unless the running SAT instance finishes UNSAT. That is the leftover.

## 7. 27 August

The binomial CNF at n=18 was mostly cardinality. Sequential counters drop it from 465k clauses to 13k. Split by k=|N⁻(0)|, with N⁻(0) labelled {7,…,6+k}. High k dies immediately: each v in N⁺(0) has only 16−k legal out-targets.

k=1 through k=11 came back UNSAT. k=1 took 587s and a 1.2 GB DRAT that `drat-trim` accepted. k=6..11 have tiny stored proofs. k=2..5 were verified and the large proofs dropped.

The k=0 / t=6 search is leftover bookkeeping. It is not needed. A 6-outregular graph on 18 vertices has 108 arcs, so some vertex has in-degree at least 6. Put that vertex at 0. The cubes k=6..11 all have stored DRATs. That is the exact statement at n=18.

## 8. 27 August, next holes

The same counting works at every later hole. A d-outregular oriented graph has n d arcs, so some in-degree is at least d. The leftover exact orders are those with ⌈n/3⌉ < 0.3465 n, i.e. 21, 24, 26, 27, and so on.

The fear was that n=21 k=7 would be the n=18 k=1 situation (ten minutes, a gigabyte). It was the n=18 k=6 situation: 37 milliseconds, a 59 kB DRAT. Every needed cube through n=36 died the same way. The encoder is not empty: n=21 d=6 and n=24 d=7 still SAT, with checked C₃-free models.

So the finite statement is now checked at n=21, 24, 26, 27, 29, 30, 32, 33, 35, 36. The stored proofs are the DRATs in `compute/q2/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The F₄ number did not move. The first hole not run is n=38.

## 9. 27 August, leftover holes from n=38

The same counting works at n=38. A 13-outregular oriented graph has 494 arcs, so some in-degree is at least 13. The leftover exact orders are those with ⌈n/3⌉ < 0.3465 n and n > 36.

The fear was again that n=38 k=13 would be the n=18 k=1 situation. It was the n=36 k=12 situation: 84 milliseconds, a 370 kB DRAT. Every needed cube through n=72 died the same way, the slowest about two seconds.

One false start: asking kissat to *find* the n=38 d=12 circulant under the lex cut. That search timed out at 60s. The circulant itself is explicit, C₃-free, 12-outregular, and after placing the in- and out-neighbourhoods of 0 it satisfies every arc-variable clause of the cube, including the lex units. So the encoder is not empty at this order. The small-n SAT pair n=21 d=6 k=6 still comes back SAT in 0.15s.

A numerical try: add the missing order-2 type (two vertices, no arc) as a second 9×9 Cauchy–Schwarz block inside F₄. The old certificate at 0.34645 still works. Nothing at 0.346 or below does. The extra SOS is not a new threshold.

The stored proofs are the 534 DRATs in `compute/q3/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The F₄ number did not move. The first hole not run is n=73.

## 10. 27 August, leftover holes from n=73

The same counting works at n=73. A 25-outregular oriented graph has 1825 arcs, so some in-degree is at least 25. After n=72 every leftover n is consecutive: HKN 0.3465 already implies the n≡1 (mod 3) orders through about n=50, and after that ⌈n/3⌉ stays below 0.3465 n.

n=73 k=25 was 1.08s and 5244 conflicts with lex SB, not the n=18 k=1 situation. Every needed cube through n=108 died the same way, the slowest about 27 seconds. Raw kissat proofs at n≈84+ grew past 100 MB; `drat-trim` core lemmas (binary) still replay against a regenerated CNF and fit in the repo.

The encoder is not empty. n=21 d=6 k=6 is SAT in 0.15s with a checked C₃-free model. The n=73 circulant (degree 24) satisfies the cube clauses after the neighbourhoods of 0 are placed.

A numerical try that did move: replace CSS β≤γ in the HKN fork by Chen–Karson–Liu–Shen 2015, β<0.8616γ. Same 32 types, same 4Ψ(κ) coefficients, stronger uniform penalty. The stored certificate at 0.34645 still works. A new ray certifies **c=0.34640** (worst F=−0.419 at r₃₀). Nothing at 0.346 or 0.3388 does. HKN said this tightening of Lemma 3.5 would only produce a tiny decrease. That is the move.

The stored proofs are the 1026 DRATs in `compute/q4/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=109. The conjecture 1/3 is open.

## 11. 27 August, leftover holes from n=109

The same cubes keep dying past n=108. A 37-outregular oriented graph on 109 vertices has 4033 arcs, so some in-degree is at least 37. The needed k are 37 through 70; k=71 is empty by the N⁺ counting cut.

n=109 k=37 is the old leftover hole from the n=108 wrap. It is UNSAT, and so is every later leftover order through n=114. Independent replay of those 213 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay.

A numerical try that did not move: the stored CKLS-fork ray at 0.34640 already has worst F positive at 0.34639. Warm Qs, extra forms, and a CSS reading 1/(1+0.16065) do not produce a new certificate. F₄ stays 0.34640.

The stored proofs for this range are the 213 DRATs in `compute/q5/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=115. The conjecture 1/3 is open.

## 12. 27 August, leftover holes from n=115

The same cubes keep dying past n=114. A 39-outregular oriented graph on 115 vertices has 4485 arcs, so some in-degree is at least 39. The needed k are 39 through 74; k=75 is empty by the N⁺ counting cut.

n=115 k=39 is the old leftover hole from the n=114 wrap. It is UNSAT. Independent replay of those 36 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=40 core stays about 10 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 36 DRATs in `compute/q6/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=116. The conjecture 1/3 is open.

## 13. 27 August, leftover holes from n=116

The same cubes keep dying past n=115. A 39-outregular oriented graph on 116 vertices has 4524 arcs, so some in-degree is at least 39. The needed k are 39 through 75; k=76 is empty by the N⁺ counting cut.

n=116 k=39 is the old leftover hole from the n=115 wrap. It is UNSAT. Independent replay of those 37 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 37 DRATs in `compute/q7/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=117. The conjecture 1/3 is open.

## 14. 27 August, leftover holes from n=117

The same cubes keep dying past n=116. A 39-outregular oriented graph on 117 vertices has 4563 arcs, so some in-degree is at least 39. The needed k are 39 through 76; k=77 is empty by the N⁺ counting cut.

n=117 k=39 is the old leftover hole from the n=116 wrap. It is UNSAT. Independent replay of those 38 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=40 core stays about 9 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 38 DRATs in `compute/q8/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=118. The conjecture 1/3 is open.

## 15. 27 August, leftover holes from n=118

The same cubes keep dying past n=117. A 40-outregular oriented graph on 118 vertices has 4720 arcs, so some in-degree is at least 40. The needed k are 40 through 76; k=77 is empty by the N⁺ counting cut.

n=118 k=40 is the old leftover hole from the n=117 wrap. It is UNSAT. Independent replay of those 37 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=74 core stays about 7.5 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 37 DRATs in `compute/q9/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=119. The conjecture 1/3 is open.

## 16. 27 August, leftover holes from n=119

The same cubes keep dying past n=118. A 40-outregular oriented graph on 119 vertices has 4760 arcs, so some in-degree is at least 40. The needed k are 40 through 77; k=78 is empty by the N⁺ counting cut.

n=119 k=40 is the old leftover hole from the n=118 wrap. It is UNSAT. Independent replay of those 38 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=75 core stays about 7.6 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 38 DRATs in `compute/q10/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=120. The conjecture 1/3 is open.

## 17. 27 August, leftover holes from n=120

The same cubes keep dying past n=119. A 40-outregular oriented graph on 120 vertices has 4800 arcs, so some in-degree is at least 40. The needed k are 40 through 78; k=79 is empty by the N⁺ counting cut.

n=120 k=40 is the old leftover hole from the n=119 wrap. It is UNSAT. Independent replay of those 39 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=40 core stays about 25 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 39 DRATs in `compute/q11/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=121. The conjecture 1/3 is open.

## 18. 27 August, leftover holes from n=121

The same cubes keep dying past n=120. A 41-outregular oriented graph on 121 vertices has 4961 arcs, so some in-degree is at least 41. The needed k are 41 through 78; k=79 is empty by the N⁺ counting cut.

n=121 k=41 is the old leftover hole from the n=120 wrap. It is UNSAT. Independent replay of those 38 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=41 core stays about 9 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 38 DRATs in `compute/q12/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=122. The conjecture 1/3 is open.

## 19. 27 August, leftover holes from n=122

The same cubes keep dying past n=121. A 41-outregular oriented graph on 122 vertices has 5002 arcs, so some in-degree is at least 41. The needed k are 41 through 79; k=80 is empty by the N⁺ counting cut.

n=122 k=41 is the old leftover hole from the n=121 wrap. It is UNSAT. Independent replay of those 39 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=45 core stays about 7 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 39 DRATs in `compute/q13/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=123. The conjecture 1/3 is open.

## 20. 27 August, leftover holes from n=123

The same cubes keep dying past n=122. A 41-outregular oriented graph on 123 vertices has 5043 arcs, so some in-degree is at least 41. The needed k are 41 through 80; k=81 is empty by the N⁺ counting cut.

n=123 k=41 is the old leftover hole from the n=122 wrap. It is UNSAT. Independent replay of those 40 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=41 core stays about 12 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 40 DRATs in `compute/q14/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=124. The conjecture 1/3 is open.

## 21. 27 August, leftover holes from n=124

The same cubes keep dying past n=123. A 42-outregular oriented graph on 124 vertices has 5208 arcs, so some in-degree is at least 42. The needed k are 42 through 80; k=81 is empty by the N⁺ counting cut.

n=124 k=42 is the old leftover hole from the n=123 wrap. It is UNSAT. Independent replay of those 39 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=44 core stays about 11 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 39 DRATs in `compute/q15/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=125. The conjecture 1/3 is open.

## 22. 27 August, leftover holes from n=125

The same cubes keep dying past n=124. A 42-outregular oriented graph on 125 vertices has 5250 arcs, so some in-degree is at least 42. The needed k are 42 through 81; k=82 is empty by the N⁺ counting cut.

n=125 k=42 is the old leftover hole from the n=124 wrap. It is UNSAT. Independent replay of those 40 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=44 core stays about 9 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 40 DRATs in `compute/q16/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=126. The conjecture 1/3 is open.

## 23. 27 August, leftover holes from n=126

The same cubes keep dying past n=125. A 42-outregular oriented graph on 126 vertices has 5292 arcs, so some in-degree is at least 42. The needed k are 42 through 82; k=83 is empty by the N⁺ counting cut.

n=126 k=42 is the old leftover hole from the n=125 wrap. It is UNSAT. Independent replay of those 41 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=45 core stays about 6 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 41 DRATs in `compute/q17/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=127. The conjecture 1/3 is open.

## 24. 27 August, leftover holes from n=127

The same cubes keep dying past n=126. A 43-outregular oriented graph on 127 vertices has 5461 arcs, so some in-degree is at least 43. The needed k are 43 through 82; k=83 is empty by the N⁺ counting cut.

n=127 k=43 is the old leftover hole from the n=126 wrap. It is UNSAT. Independent replay of those 40 cubes is 0 failures. Raw kissat proofs again grow past 100 MB; `drat-trim` core lemmas still replay. The k=47 core stays about 12 MB.

A numerical try that did not move: F₄ stays 0.34640 at the stored CKLS-fork ray.

The stored proofs for this order are the 40 DRATs in `compute/q18/certs/keep/`. Replay regenerates each CNF and runs `drat-trim`. The first hole not run is n=128. The conjecture 1/3 is open.


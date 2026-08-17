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

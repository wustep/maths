# Research log — Caccetta–Häggkvist for directed triangles

## 2026-08-17

Fetched and read tonight, in the order used.

### The conjecture

Caccetta–Häggkvist (1978): every simple n-vertex digraph of minimum out-degree at least r has a directed cycle of length at most ⌈n/r⌉. The first open case is r = n/3: every n-vertex oriented graph with δ⁺ ≥ n/3 has a directed triangle. (2-cycles already have length 2, so one reduces to oriented graphs.)

AIM workshop summary: Blair D. Sullivan, *A Summary of Results and Problems Related to the Caccetta-Häggkvist Conjecture* (14 Apr 2006). Local: `compute/refs/sullivan-aim-caccetta.pdf`. The Egres page timed out.

### Published out-degree thresholds for a triangle

| c | source | notes |
| --- | --- | --- |
| (3−√5)/2 ≈ 0.3820 | Caccetta–Häggkvist 1978 | original paper |
| (2√6−3)/5 ≈ 0.3798 | Bondy, *Discrete Math.* 1997 | subgraph counting |
| 3−√7 ≈ 0.3542 | Shen, *J. Combin. Theory Ser. B* 74 (1998) | one page |
| 0.3532 | Hamburger–Haxell–Kostochka, *Electron. J. Combin.* 14 (2007) | uses Chudnovsky–Seymour–Sullivan; local `compute/refs/hamburger-haxell-kostochka-eljc.pdf` |
| **0.3465** | Hladký–Král'–Norin, *Combinatorica* 37 (2017); arXiv:0908.2791v4 | flag algebras on F₄ + induction + CSS. Ancillary `CH.mw`. Local `compute/refs/hladky-kral-norin-0908.2791.pdf` |
| 0.3388 | de Joannis de Verclos–Sereni–Volec, March 2014 | **personal communication**. HKN v4 footnote; Grzesik–Volec IMRN 2023 [18]. F₆, no public file |
| 0.343545 (two-sided) | Lichiardopol, *Discrete Math.* 2010 | both δ⁺ and δ⁻; different theorem |

Grzesik–Volec, *Degree conditions forcing directed cycles*, IMRN 2023 / arXiv:2102.12830v2, still quote HKN 0.3465 as the published unrestricted bound and mention 0.3388 only as a personal communication. Local `compute/refs/grzesik-volec-2102.12830.pdf`.

### Exact r, additive error, classes

- r=2: Caccetta–Häggkvist 1978.
- r=3: Hamidoune, JCTB 1987.
- r=4 and r=5: Hoàng–Reed, *Discrete Math.* 66 (1987).
- n ≥ 2r² − 3r + 1: Shen, *Discrete Math.* 2000. Finitely many exceptions per r. For r=6 this is n≥55, so it does not touch the triangle case at n=18.
- Cycle length ≤ n/r + 73: Shen, *Graphs Combin.* 2002.
- Cayley / vertex-transitive: Hamidoune. No circulant counterexample.

Razborov, arXiv:math/0604317: the conjecture holds if three specific 4-vertex digraphs are forbidden. Local `compute/refs/razborov-math0604317.pdf`. Not used tonight.

Behzad–Chartrand–Wall (regular girth-g cages) is implied by CH. Not attacked separately.

### The cyclic construction

Out-neighbours {1,…,⌊(n−1)/3⌋} on ℤ/nℤ. C₃-free because three steps sum to at most 3⌊(n−1)/3⌋ < n. This meets the conjectured max min-outdegree, so the exact finite statement is δ⁺ ≥ ⌈n/3⌉ ⇒ C₃.

### What HKN actually certify

Theorem 3.3: every homomorphism of the flag algebra of triangle-free oriented graphs has δα < 0.3465. The proof is emptiness of a set R(c) ⊂ ℝ³² of 4-vertex type densities, via a linear combination of

- 8×8 Cauchy–Schwarz on β-flags (Table 1),
- 14 out-regularity identities (Table 2),
- two order-3 induction forms (4.14), (4.15),
- a CSS-fork inequality.

Tonight independently rebuilt every matrix and linear form (`flags4.py`, `ind_fork.py`). They match. The printed two-decimal aᵢ do not reproduce the printed expansion (4.22). Re-optimising the combination on the rebuilt system, the F₄ threshold is ≈ 0.346439. A stored certificate at **0.34645** (worst F = −0.12343) is `certs/f4_certificate.json`.

### What we compare against

- Refereed unrestricted threshold: HKN **0.3465**. Tonight 0.34645, same method, independent matrices. Fifth decimal only. Did **not** beat 0.3388.
- Exact small n: Hoàng–Reed covers ⌈n/3⌉ ≤ 5, i.e. n≤15. HKN covers every n with ⌈n/3⌉ ≥ 0.3465 n, so the first open exact order is **n=18, d=6**. Tonight DRAT-verified the exact statement at n=12, 15, 16, 17. n=16 is the first n with d=6; HKN already implies n=16 and n=17. n=18 is the residue.

### False or unused full-proof claims

None used. The 0.3388 communication is not taken as a theorem for the purpose of claiming a new threshold.

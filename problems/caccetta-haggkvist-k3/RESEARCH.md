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

## 2026-08-27

Opened tonight, in order.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016, final Combinatorica text. Abstract and Theorem 1.2: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. No later version.
- https://arxiv.org/html/0908.2791v4 — same paper, HTML. Theorem 3.3: max δα(Ψ) < 0.3465 on Hom⁺ of the triangle-free flag algebra. Footnote still records the March 2014 personal communication 0.3388 (F₆); that number is not a theorem in this file.
- https://arxiv.org/abs/2102.12830 — Grzesik–Volec v2, 18 Jan 2024. Semidegree thresholds for directed cycles of length ≠ 3. Does not replace the unrestricted triangle threshold.
- https://arxiv.org/html/2102.12830v2 — same. Still states the original CH triangle case as open, quotes the classical 0.3820 bound in the survey paragraph, and does not publish a new unrestricted c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash, 26 Feb 2024, *On the length of directed paths in digraphs*. Theorem 9 quotes HKN: every oriented graph of order n and minimum out-degree 0.3465n contains a directed triangle. No new unrestricted c.
- https://www.proofatlas.ai/collaboration/caccetta-haggkvist-conjecture/ — status checked 2 Aug 2026. Peer-reviewed unrestricted triangle threshold still listed as HKN 0.3465n. Conjecture open.
- http://www2.im.uj.edu.pl/AndrzejGrzesik/CH/CH.pdf — Grzesik–Volec slides/notes on the T₅-free case. Cites HKN 0.3465 and “Sereni and Volec [27] stated even further improvement to 0.3388”. That is the same personal communication, not a paper.
- https://www.combinatorics.org/ojs/index.php/eljc/article/download/v24i2p19/pdf — Grzesik–Volec, *Electron. J. Combin.* 24 (2017), CH with a forbidden T₅. Same 0.3388 sentence. Restricted class; not the unrestricted threshold.
- https://arxiv.org/pdf/1112.3477 — Lichiardopol, two-sided / connectivity refinements. Uses HKN 0.3465 as input. Different theorem (semidegree).
- https://www.sciencedirect.com/science/article/pii/S0012365X10003043 — Lichiardopol, *Discrete Math.* 2010, two-sided 0.343545. Already in the 17 August table; not unrestricted.

Failed lookup: no arXiv hit after 2024 that states a published unrestricted c < 0.3465 with a public certificate. The 0.3388 figure remains a personal communication.

Replay tonight: the stored F₄ certificate at c=0.34645 still has min eig(Q)=9.53e-9 and worst F=−0.12343. The same ray is negative at 0.34644447 and positive at 0.34644, so this system does not give a clean step below 0.34645.

## 2026-08-27 — q2 literature

Opened tonight, in order, before the n=21 SAT.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract and Theorem 1.2 still: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. No v5.
- https://export.arxiv.org/api/query?id_list=0908.2791 — same record via the API.
- https://arxiv.org/abs/2102.12830 — Grzesik–Volec v2, 18 Jan 2024. Semidegree thresholds for directed cycles of length ≠ 3. Does not publish a new unrestricted triangle c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash v4, 21 Aug 2024. Path lengths under a girth hypothesis. Theorem 9 quotes HKN 0.3465 as the triangle-case input. No new unrestricted c.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending — newest unrestricted-looking hits are Cheng–Keevash 2402.16776v4 and Raz 2405.17797 (second-neighbourhood / anti-transitive, not a triangle-threshold paper). No post-2017 paper in that list states a published unrestricted c < 0.3465.

Failed lookup: no later Combinatorica / IMRN replacement of HKN 0.3465 with a public certificate. The 0.3388 figure remains a personal communication.

## 2026-08-27 — q3 literature

Opened tonight, in order, before the n=38 SAT.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract and Theorem 1.2 still: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. No v5.
- https://arxiv.org/html/0908.2791v4 — same paper. Theorem 1.2 is the 0.3465n statement; Theorem 3.3 is emptiness of R(0.3465) in the triangle-free flag algebra. Footnote still records the March 2014 personal communication 0.3388 (F₆); that number is not a theorem in this file.
- https://export.arxiv.org/api/query?id_list=0908.2791 — same record via the API.
- https://arxiv.org/abs/2102.12830 — Grzesik–Volec v2, 18 Jan 2024. Semidegree thresholds for directed cycles of length ≠ 3. Does not publish a new unrestricted triangle c.
- https://arxiv.org/html/2102.12830v2 — same. Still states the original CH triangle case as open.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash v4, 21 Aug 2024. Path lengths under a girth hypothesis. Uses HKN 0.3465 as the triangle-case input. No new unrestricted c.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch, 28 May 2024. Second-neighbourhood / anti-transitive class. A restricted-class CH consequence, not a new unrestricted c.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending — newest hits are still Cheng–Keevash 2402.16776v4 and Mezher–Daamouch 2405.17797. No post-2017 paper in that list states a published unrestricted c < 0.3465.

Failed lookup: no later Combinatorica / IMRN replacement of HKN 0.3465 with a public certificate. The 0.3388 figure remains a personal communication. Do not treat it as published.

## 2026-08-27 — q4 literature

Opened tonight, in order, before the n=73 SAT and the CKLS-fork replay.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract and Theorem 1.2 still: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. No v5.
- https://arxiv.org/html/0908.2791v4 — same. Theorem 3.3: max δα(Ψ) < 0.3465. Lemma 3.4 is deg⁺ < √(2k) from CSS β≤γ. Lemma 4.7 is Ψ(κ)≥3(3c₀−1)². The closing remark records DHP 0.88 and a Shen private 0.865 as improvements of Lemma 3.5 that “only produce a tiny decrease” in Theorem 1.2; they did not publish that smaller number. Footnote still records the March 2014 personal communication 0.3388 (F₆).
- https://arxiv.org/abs/2102.12830 — Grzesik–Volec v2, 18 Jan 2024. Semidegree thresholds for directed cycles of length ≠ 3.
- https://arxiv.org/html/2102.12830v2 — Theorem 2.2 quotes HKN: every n-vertex oriented graph with δ⁺ ≥ 0.3465n contains C₃. Note: de Joannis de Verclos–Sereni–Volec [18] “established an improvement to 0.3388n”; bibliography [18] is personal communication. Does not replace the unrestricted triangle number.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash v4, 21 Aug 2024. Path lengths under a girth hypothesis. Uses HKN 0.3465 as the triangle-case input. No new unrestricted c.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch, 28 May 2024. Second-neighbourhood / 7-anti-transitive class. A restricted-class CH consequence, not a new unrestricted c.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract: β(G) ≤ 0.8616 γ(G) for 3-free digraphs, improving DHP 0.88.
- https://arxiv.org/html/0909.2468 — same. Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G). Published as *Electron. J. Linear Algebra* 28 (2015).
- https://www.combinatorics.org/ojs/index.php/eljc/article/download/v14i1n19/pdf — Hamburger–Haxell–Kostochka, *Electron. J. Combin.* 14 (2007). Lemma 5: a triangle-free orientation obtained from a tournament by deleting k edges has a vertex of out-degree < √(2k).
- https://www.proofatlas.ai/collaboration/caccetta-haggkvist-conjecture/ — checked tonight. Peer-reviewed unrestricted triangle threshold still listed as HKN 0.3465n. Conjecture open.

Failed lookup: no later Combinatorica / IMRN replacement of HKN 0.3465 with a public certificate. The 0.3388 figure remains a personal communication. Do not treat it as published.

## 2026-08-27 — F-coordinate dump, lemma chain

Re-opened for the independent 4Ψ(κ) / F₄ dump (no SAT).

- https://arxiv.org/html/0908.2791v4 — HKN Lemmas 3.4, 3.5, 4.6, 4.7 read in full. Lemma 3.4: k non-edges ⇒ some deg⁺ < √(2k). Lemma 3.5: P[Ψ^λ(α) < √(1−Ψ(ρ))+ε] > 0. Lemma 4.6: Φ(γ) ≥ c₀ − √(Φ(χ)). Lemma 4.7: Ψ(κ) ≥ 3(3c₀−1)², then (4.7) expands 4Ψ(κ−3(3c₀−1)²). Closing remark: DHP 0.88 / Shen 0.865 improve Lemma 3.5 and “only produce a tiny decrease”.
- https://arxiv.org/abs/0908.2791 — same v4 record.
- https://arxiv.org/html/0909.2468 — CKLS Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G). Proof uses μ=0.16065 and 1/(1+μ)=0.8616.
- https://arxiv.org/abs/0909.2468 — abstract writes β ≤ 0.8616 γ (theorem statement is strict).
- https://www.combinatorics.org/ojs/index.php/eljc/article/download/v14i1n19/pdf — HHK Lemma 5: triangle-free orientation from a tournament minus k edges has a vertex of out-degree < √(2k). The count is 1+⋯+m ≤ k after deleting k feedback arcs (their Lemma 4 / CSS). Replacing the budget k by 0.8616 k gives < √(2·0.8616 k).

## 2026-08-27 — wrap re-open (leftover through n=108)

Opened again before wrapping the leftover-SAT claim against the published record.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract and Theorem 1.2 still: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. No v5.
- https://arxiv.org/html/0908.2791v4 — same. Theorem 1.2 is the 0.3465n statement. The closing remark still records the March 2014 personal communication 0.3388 (F₆) and says DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=113)

Opened again before wrapping leftover SAT past n=108.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=15 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/html/2405.17797 — same restricted statement.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n; they do not replace it.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=115)

Opened again before wrapping leftover SAT past n=114.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=15 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=116)

Opened again before wrapping leftover SAT past n=115.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=15 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=117)

Opened again before wrapping leftover SAT past n=116.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=118)

Opened again before wrapping leftover SAT past n=117.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=119)

Opened again before wrapping leftover SAT past n=118.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=120)

Opened again before wrapping leftover SAT past n=119.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=121)

Opened again before wrapping leftover SAT past n=120.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=122)

Opened again before wrapping leftover SAT past n=121.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=123)

Opened again before wrapping leftover SAT past n=122.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ. The same page includes Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://arxiv.org/html/0909.2468 — Internal Server Error this session.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.

## 2026-08-27 — wrap re-open (leftover through n=124)

Opened again before wrapping leftover SAT past n=123.

- https://arxiv.org/abs/0908.2791 — Hladký–Král'–Norin v4, 22 Feb 2016. Abstract: every n-vertex digraph of minimum out-degree 0.3465n contains an oriented triangle. Journal reference Combinatorica 37 (2017). No v5.
- https://arxiv.org/html/0908.2791v4 — Theorem 1.2 is the 0.3465n statement. Closing remark: de Joannis de Verclos–Sereni–Volec 0.3388 in March 2014 by F₆ (personal communication); DHP 0.88 / Shen 0.865 only produce a tiny decrease in Theorem 1.2.
- https://arxiv.org/abs/0909.2468 — Chen–Karson–Liu–Shen. Abstract writes β ≤ 0.8616 γ. The same page includes Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://arxiv.org/html/0909.2468 — Theorem 2.5: if G is 3-free then β(G) < 0.8616 γ(G), with μ=0.16065.
- https://export.arxiv.org/api/query?search_query=all:Caccetta+AND+all:Haggkvist&sortBy=submittedDate&sortOrder=descending&max_results=10 — 10 hits. Newest unrestricted-looking items are still 2405.17797 and 2402.16776v4. No post-2017 paper in that list states a published unrestricted c < 0.3465.
- https://arxiv.org/abs/2405.17797 — Mezher–Daamouch. Restricted: a special case of Caccetta–Häggkvist on 7-anti-transitive oriented graphs (via Seymour vertices). No unrestricted numerical c.
- https://arxiv.org/abs/2402.16776 — Cheng–Keevash. Path-length bounds that *use* HKN 0.3465n (their Theorem 9); they do not replace it.
- https://arxiv.org/html/2402.16776 — Theorem 9 quotes HKN 0.3465n.

Failed lookup: no later Combinatorica replacement of HKN 0.3465. Do not treat 0.3388 as published.



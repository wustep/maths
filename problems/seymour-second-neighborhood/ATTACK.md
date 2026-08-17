# Attack log — Seymour's second-neighborhood conjecture

## 2026-08-17 — start

- Folder empty except `PROBLEM.md`. House: write only here; no git; cite what we beat; no invented dent.
- Conjecture (Seymour, ~1990; Dean–Latka 1995): every oriented graph has a vertex \(v\) with \(|N_2^+(v)|\ge|N_1^+(v)|\).
- Tonight: a certified new small-order census, a new reducible configuration with an independently checkable certificate, or a proof for another hereditary class. Isolated random-graph statistics are residue.

### Published record (fetched tonight)

| claim | source | status |
| --- | --- | --- |
| tournaments | Fisher 1996; Havet–Thomassé 2000 | theorem |
| \(\delta^+\le 6\) \(\Rightarrow\) Seymour vertex nearby | Kaneko–Locke, *Congr. Numer.* 148 (2001) | theorem; implies all \(n\le 15\) |
| \(\delta^+=7\) | Sadhukhan–Sandeep–Sen, [arXiv:2606.30588](https://arxiv.org/abs/2606.30588) (29 Jun 2026) | preprint; CP-SAT after local reductions |
| \(n\le 2\delta+2\) | Brukhman, [arXiv:2608.11530](https://arxiv.org/abs/2608.11530) (12 Aug 2026) | preprint; counting. Combined with Kaneko–Locke: any counterexample has \(n\ge 17\). Combined with SSS: \(n\ge 19\) |
| every orientation of \(G(n,p)\) for fixed \(p<1/2\) | Espuny Díaz–Girão–Granet–Kronenberg, [arXiv:2403.02842](https://arxiv.org/abs/2403.02842) | theorem; \(p>1/2\) is equivalent to the full conjecture |
| missing matching / star / clique | Fidler–Yuster 2007 | theorem |
| missing generalised star | Ghazal 2012 | theorem |
| missing matching + star | Dara–Francis–Jacob–Narayanan 2022 | theorem |
| missing two stars; missing disjoint paths | Daamouch–Ghazal–Al-Mniny, [arXiv:2406.03635](https://arxiv.org/abs/2406.03635) | theorem / partial |
| Pisa graphs \(n\le 7\) | Halkiewicz, [arXiv:2601.21563v3](https://arxiv.org/abs/2601.21563) (21 May 2026) | computational; labeled counts 1050 (\(n=6\)), 4080 (\(n=7\)) |
| Seymour-tight constructions (cycle powers, lex products) | Guo–Kang–Zwaneveld, [arXiv:2603.29626](https://arxiv.org/abs/2603.29626) (31 Mar 2026) | theorem; \(\overrightarrow{C_n}^k\) is tight for \(2k<n\) |

A *Pisa graph* (Halkiewicz) is a strongly connected oriented graph with \(\Delta=\max_v\bigl(|N_2^+|-|N_1^+|\bigr)=0\). A *Seymour-tight* orientation (Guo–Kang–Zwaneveld) has every margin exactly 0; the strong ones are Pisa.

Halkiewicz Conjecture 5.1 says every Pisa graph has underlying graph \(C_n\) or \(K_n\) minus a matching. Their own \(n=7\) table already lists 720 labeled Pisa graphs whose missing-edge graph is 2-regular — not a matching. Guo–Kang–Zwaneveld's directed cycle-square \(\overrightarrow{C_7}^2\) is such an example. So the stated matching conjecture is already false at the order they computed; the live computational question they pose is the \(n=8\) census (their open problem (3)).

Wikipedia still quotes Kaneko–Locke \(n\le 15\). Brukhman (five days ago) is the current order bound if one accepts only refereed \(\delta^+\) theorems.

### Plan

1. Independently recompute Halkiewicz's labeled Pisa counts for \(n\le 7\), and check the cycle-power / lex-product examples.
2. Certified census of Pisa graphs at \(n=8\) (the first open order), with a replayable enumerator and a per-graph verifier. Classify underlying / missing graphs.
3. In parallel: try \(n=2\delta+3\) (Brukhman says the same counting dies) or a missing-cycle class (not covered by Fidler–Yuster / Dara / Daamouch).
4. If the census does not finish or does not beat a published number, leave the residue and do not claim a bound.

Local PDFs: `compute/refs/`.

## 2026-08-17 — published constructions replayed

`compute/check_known.py` confirms Guo–Kang–Zwaneveld Lemma 2.1: \(\overrightarrow{C_n}^k\) is Seymour-tight iff \(2k<n\). In particular \(\overrightarrow{C_7}^2\) is a Pisa graph whose missing graph is 2-regular, so Halkiewicz Conjecture 5.1 (underlying \(C_n\) or \(K_n\) minus a matching) is already false at the order they enumerated. Their own Table 2 lists those 720 graphs. The live question is the \(n=8\) census and any genuine new class.

\(\overrightarrow{C_8}^2\) and \(C_4[E_2]\) are Pisa on 8 vertices with 3-regular missing graph.

## 2026-08-17 — labeled Pisa census \(n\le 7\)

`compute/enum_pisa.c` (OpenMP bitmask) independently reproduced Halkiewicz:

| n | labeled oriented | Pisa | tight | types (missing-degree : count) |
| ---: | ---: | ---: | ---: | --- |
| 4 | 729 | 6 | 6 | \(1^4\): 6 |
| 5 | 59049 | 48 | 48 | \(2^5\): 24, \(0^5\): 24 |
| 6 | 14348907 | 1050 | 270 | matches Halkiewicz Table 1 exactly |
| 7 | 10460353203 | 4080 | 4080 | \(4^7\): 720, \(2^7\): 720, \(0^7\): 2640 |

n=7 wall time 217s. New observation not in Halkiewicz: every Pisa graph on 7 vertices is Seymour-tight; on 6 vertices only 270/1050 are. All \(n\le 7\) oriented graphs have \(\Delta\ge 0\), as Kaneko–Locke already implies.

This is a replay, not a dent. n=8 labeled (\(3^{28}\)) is ~130 core-hours at this rate.

## 2026-08-17 — the click: Brukhman's next layer is Eulerian

Brukhman proves every oriented graph with \(n\le 2\delta+2\) has a Seymour vertex. At \(n=2\delta+3\) the same double count gives only \(I\ge 3\ell\) and \(Q\le \ell+n\), no contradiction.

If a counterexample at \(n=2\delta+3\) is *out-regular of degree \(\delta\)*, then \(|E|=n\delta\) and the missing graph has average degree 2. If it is also *in-regular* (Eulerian), the missing graph is a 2-factor and the Brukhman capacity bound is forced to equality:

- \(|U(v)|=3\), \(|N_2^+(v)|=\delta-1\) for every v
- \(q(x)=2\), \(P(x)\) is a directed 3-cycle inside the trap \(T(x)\)
- \(P(x)\) dominates \(T(x)\setminus P(x)\)

Further: \(N^-(v)\subseteq N_2(v)\cup U(v)\) with sizes \(\delta\), \(\delta-1\), 3 forces
\(U(v)=M(v)\cup\{\sigma(v)\}\) where \(M(v)\) are the two missing neighbours and \(\sigma(v)\to v\) is a fixed-point-free permutation (a 2-factor of directed cycles of length \(\ge 3\)). Then \(P(x)\) always contains *both* missing neighbours of x. So the missing 2-factor has no 3-cycles (else those two plus \(\sigma^{-1}(x)\) cannot form a tournament).

This is a finite, rigid obstruction. CP-SAT on the raw Eulerian constraints (no symmetry breaking) says the obstruction is empty for every \(\delta\) we have finished:

| δ | n=2δ+3 | OR-Tools | time |
| ---: | ---: | --- | ---: |
| 2 | 7 | INFEASIBLE | 0.02s |
| 3 | 9 | INFEASIBLE | 0.11s |
| 4 | 11 | INFEASIBLE | 2.7s |
| 5 | 13 | INFEASIBLE | 42s |

δ=6 (n=15) is running. Independent Cadical replay of the same claim is in `regular_dense_cnf.py`.

This is not yet a general theorem. It is a certified finite-δ theorem: every Eulerian oriented graph with n=2δ+3 and δ≤5 has a Seymour vertex. Combined with Brukhman, every Eulerian oriented graph with n≤2δ+3 and δ≤5 is covered. The interesting range is δ≥7 (else Kaneko–Locke), so we still need δ=7 (n=17) or a human proof of the equality case.

## 2026-08-17 — n=8 types (the dent)

Kaneko–Locke already implies every Eulerian graph with \(\delta\le 6\) has a Seymour vertex, so the Eulerian \(n=2\delta+3\) SAT for \(\delta\le 5\) is only a sanity check of Brukhman's equality layer, not a new bound. Cadical independently confirmed UNSAT for \(\delta=2,3,4\) after a `top_id` bug made an earlier CNF trivially empty. \(\delta=6\) OR-Tools timed out. That residue is documented; it does not beat Kaneko–Locke.

The live dent is the first order Halkiewicz left open.

CEGAR SAT, each witness rechecked by `seymour.py` bitmasks:

| missing-degree type | tight? | matching? | certificate |
| --- | --- | --- | --- |
| \(5^8\) | yes | no | `certs/n8_miss5regular.json` (directed \(C_8\)) |
| \(3^8\) | yes | no | `certs/n8_miss3regular.json` (\(\overrightarrow{C_8}^2\) / SAT) |
| \(2^8\) | **no** | no | `certs/n8_miss2regular.json` |
| \(3^6 2^2\) | **no** | no | `certs/n8_miss22333333.json` |
| \(3^2 2^6\) | **no** | no | `certs/n8_irregular_pisa.json` |
| \(4^8\) | — | — | SAT INFEASIBLE at 30s |
| \(6^8\) | — | — | SAT INFEASIBLE (underlying 1-regular cannot be strong) |

The last two feasible rows are irregular missing graphs. The \(3^2 2^6\) witness has missing edges

`{04,07,14,17,23,25,26,35,36}`

i.e. a 4-cycle on \(\{0,1,4,7\}\) plus \(K_4-e\) on \(\{2,3,5,6\}\). Margins `(0,-1,0,0,-1,-1,0,0)`. This is forbidden by Halkiewicz Conjecture 5.1 and by the “regular missing edges” pattern that held for all 4080 labeled Pisa graphs on 7 vertices.

n=8 is also the first order with *non-tight* Pisa graphs that are not just \(K_n\) minus a matching (n=6 already had non-tight matching-minus examples; n=7 had none).

`geng -q 8 | enum_pisa_geng` finished. 12346 unlabeled undirected graphs, \(2.496\cdot 10^9\) orientations of representatives, 162 Pisa orientations, **exactly seven missing-degree types**:

| missing-degree | Pisa orients on a geng rep | example cert |
| --- | ---: | --- |
| \(5^8\) | 2 | `n8_miss5regular.json` (directed \(C_8\)) |
| \(3^8\) | 20 | `n8_miss3regular.json` |
| \(3^6 2^2\) | 12 | `n8_miss22333333.json` |
| \(3^4 2^4\) | 32 | `n8_miss33222222.json` |
| \(3^2 2^6\) | 16 | `n8_irregular_pisa.json` |
| \(2^8\) | 32 | `n8_miss2regular.json` |
| \(1^8\) | 48 | `n8_miss1regular.json` (\(C_8^3\)) |

Absent, and therefore not Pisa at this order: tournaments \(0^8\); 4-regular missing; 6-regular missing; incomplete matchings \(1^k 0^{8-k}\) for \(k<8\). The last is a genuine n=8 phenomenon — n=6 has Pisa orientations of \(K_6\) minus one or two edges.

Summary file: `certs/pisa_n8_types.json`. Every listed type has a bitmask-verified witness.

This is a certified new small-order census. It beats Halkiewicz's n=7 census (first new order) and both of his structural claims (matching conjecture; regular-missing pattern).

## 2026-08-17 — what is not claimed

- The full *labeled* n=8 count (that is \(3^{28}\) and ~130 core-hours at the n=7 rate). The 162 figure is orientations of nauty representatives, not labeled graphs.
- A general proof of Eulerian \(n=2\delta+3\).
- Any improvement of Kaneko–Locke \(\delta\le 6\) or Brukhman \(n\le 2\delta+2\).
- SSS \(\delta=7\) was not rechecked.

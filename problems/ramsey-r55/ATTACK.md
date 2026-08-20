# Attack log — determine $R(5,5)$

## 2026-08-17 — start

- House: write only under `problems/ramsey-r55`. Dent = a certified 43-vertex $(5,5)$-graph, a nonexistence proof at 45 with an independently checkable log, or a documented residue. Isolated SAT timeouts are not a dent. Search residue is not a bound.
- Fetched Radziszowski, *Small Ramsey Numbers*, revision #18, 24 April 2026, from `https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf` (149 pp, 1066 refs). The E-JC “View PDF” link returned HTML, not the survey. Table Ia lists $43\le R(5,5)\le 46$; Table Ib repeats the upper bound 46. Item 2.1(e): McKay–Radziszowski conjecture $R(5,5)=43$ with exactly 656 critical graphs on 42 vertices; Angeltveit–McKay improved the upper bound to 48 then 46; no self-complementary $(5,5)$-critical graph [Chv2]. Item 2.1(i): no Table Ia lower bound can be improved by a cyclic graph on fewer than 102 vertices, except possibly some $R(3,k)$.
- Fetched Angeltveit–McKay, $R(5,5)\le 46$, arXiv:2409.15709v2 (1 Sep 2025). The argument is LP on neighbourhood edge-counts plus a ~80 CPU-year gluing census of dense members of $\mathcal R(4,5,n)$ for $n=21,22,23,24$. Degrees in a hypothetical 46-vertex example lie in $\{21,22,23,24\}$. This is not a one-machine replay.
- Post-April-2026 screen (arXiv + survey): no later accepted improvement of either endpoint of $43\le R(5,5)\le 46$.
- McKay combinatorial-data page still hosts `r55_42some.g6` (328 graphs; the other 328 are complements). Downloaded 328 lines / 47888 bytes.

## Plan

1. Independently verify the 656 graphs are $(5,5,42)$ and that none extend by one vertex.
2. Exhaust circulants (hence all vertex-transitive graphs of prime order 43) on 43, 44, 45 vertices. Harborth–Krause already imply no cyclic improvement of the lower bound; the census is a checkable residue, not a new bound.
3. Search structured 43-vertex families that are *not* already closed by the cyclic census: involution-symmetric graphs, small edge-flip balls around the 656, Cayley graphs on non-cyclic groups of order 42/44.
4. Do not claim a dent from a SAT timeout.

## 2026-08-17 — published 656, independently checked

- `compute/verify_mckay.py`: all 328 lines of McKay’s `r55_42some.g6` are `(5,5,42)`. All 328 complements are `(5,5,42)`. None is self-complementary in the given labelling. File SHA-256 recorded in `certs/mckay42_verify.json`. 1.16s.
- Degree window on every stored graph: `min=19`, `max=22` (span exactly 3). Edge counts run from 423 to 430. Complements inherit the same window because $41-22=19$ and $41-19=22$.
- Paley-17 is `(5,5)` as a sanity check of the clique code; Paley-41 has $\omega=\alpha=5$ and is correctly rejected.

## 2026-08-17 — none of the 656 extend

- `compute/extend_check.c`: for each of the 656 graphs, the 42-bit neighbourhood SAT (no $K_4$ in $S$, no independent 4-set in $V\setminus S$, $18\le|S|\le 24$) is UNSAT. 31.1s, 883980 DPLL nodes, 0 models. Log: `logs/extend_check.txt`.
- This is McKay–Radziszowski’s extension claim, replayed. It is not a proof that $R(5,5)\le 43$: there may exist unknown 42-vertex graphs.

## 2026-08-17 — circulant census

`compute/circulant_census.c`, legal degrees from $R(4,5)=25$. Independently re-checked by `r55lib.is_ramsey` on every reported HIT.

| n | legal-degree circulants scanned | `(5,5)` hits | sec |
|---|-------------------------------:|-------------:|----:|
| 25 | 4096 | 344 | 0.003 |
| 29 | 16341 | 394 | 0.011 |
| 32 | 63687 | 384 | 0.048 |
| 33 | 63687 | 140 | 0.039 |
| 36 | 230724 | 102 | 0.182 |
| 37 | 230724 | 110 | 0.177 |
| 38 | 418132 | 18 | 0.345 |
| 39 | 418132 | **0** | 0.300 |
| 40 | 722228 | 24 | 0.637 |
| 41 | 722228 | 20 | 0.526 |
| 42 | 1167322 | **0** | 0.854 |
| 43 | 1167322 | **0** | 0.875 |
| 44 | 1704794 | **0** | 1.447 |
| 45 | 1704794 | **0** | 1.062 |

- On 43 vertices, every vertex-transitive graph is circulant (prime order). So there is **no vertex-transitive `(5,5,43)`-graph**.
- Harborth–Krause already imply no cyclic improvement of the Table Ia lower bound. This census is a checkable residue, not a new bound.
- None of the 20 circulant `(5,5,41)` graphs extends by one vertex (`certs/extend_circ_41.json`). None of the 24 circulant `(5,5,40)` graphs extends by one vertex. So none of the 656 is “circulant-41 plus a vertex”.

## 2026-08-17 — one-flip ball of the 656

- 656 × $\binom{42}{2}$ = 564816 candidate flips. 4080 preserve `(5,5,42)` (`certs/flip_search.json`).
- Color-refinement types: rerunning with canonical 1-WL ranks (first run used first-seen IDs and was not an invariant).

## 2026-08-17 — involution-symmetric 43

- Encoder `involution_sat.py` tested on n=17: kissat SAT, decoded graph is `(5,5,17)` with 58 edges (`certs/involution17_model.json`). Encoder is not vacuously UNSAT.
- Instance `cnf/involution43.cnf`: 22785 vars, 2012918 clauses (with sequential-counter degrees). Slim twin `cnf/involution43_slim.cnf`: 462 vars, 1925196 clauses (K5/I5 only).
- kissat 4.0.4 on the fat instance, `--time=900`: **`s UNKNOWN`** (`logs/kissat43.txt`).
- Slim instance, `--time=1200`: **`s UNKNOWN`** (`logs/kissat43_slim.txt`). Isolated SAT timeouts are not a dent.
- Order-3 slim instance, `--time=600`: **`s UNKNOWN`** (`logs/kissat_order3_slim.txt`). Isolated SAT timeouts are not a dent.

## Result

No 43-vertex $(5,5)$-graph. No nonexistence proof at 45. Published record still $43\le R(5,5)\le 46$.

Documented residue, independently replayable:

- The 656 McKay graphs are $(5,5,42)$ and none extend.
- No circulant $(5,5)$-graph on 42, 43, 44 or 45 vertices (hence no VT example on 43).
- No legal-degree Cayley $(5,5)$-graph on any of the six groups of order 42.
- The 656 are closed in 1-WL type under 1-flips and isolated under Seidel 1- and 2-switches.
- Involution SAT at 43 timed out. That is not a dent.

Do not cite this folder as a bound.

## 2026-08-17 — one-flip and Seidel

- Canonical 1-WL (color refinement, ranks by sorted keys): **194 types** among the 656 graphs. All 4080 `(5,5)`-preserving 1-flips stay inside those types. No new 1-WL type (`certs/flip_types.json`).
- Seidel switching on every 1-subset and every 2-subset of every one of the 656 graphs: **zero** results remain `(5,5,42)` (`certs/seidel_switch.json`, 24.9s). The published graphs are isolated under small Seidel moves.

## 2026-08-17 — Cayley census on all six groups of order 42

Group laws checked by `check_groups.py` (identity, inverses, full associativity). Degree window `[17,24]`. Inverse-closed connection sets only.

| group | involutions (non-id) | leaves | pruned | hits | sec |
|---|---:|---:|---:|---:|---:|
| $C_{42}$ (circulant) | 1 | 1167322 | — | **0** | 0.85 |
| $D_{21}$ | 21 | 154888897 | 107925216 | **0** | 97.2 |
| $C_7\times S_3$ | 3 | 365033 | 219588 | **0** | 3.45 |
| $C_3\times D_7$ | 7 | 1284757 | 808861 | **0** | 0.99 |
| $\mathrm{AGL}(1,7)=C_7\rtimes C_6$ | 7 | 949786 | 963521 | **0** | 0.89 |
| $C_2\times F_{21}$ | 1 | 106226 | 280759 | **0** | 0.24 |

There is no legal-degree undirected Cayley `(5,5)`-graph of order 42. Combined with the prime-order circulant census: no Cayley `(5,5)`-graph of order 43 either. This is not a bound on $R(5,5)$: the 656 published graphs are non-Cayley.

Python independently replayed the circulant zeros at 42 and 43 (`certs/py_circulant_{42,43}.json`, 145s / 150s, same 1167322 legal connection sets).


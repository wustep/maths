# Research note — $R(5,5)$

- Slug: `ramsey-r55`
- Date: 2026-08-17
- Published record (not beaten): $43\le R(5,5)\le 46$
- This folder: a documented search residue. No new bound.

## Published record, fetched tonight

Radziszowski, *Small Ramsey Numbers*, Electronic Journal of Combinatorics Dynamic Survey DS1, **revision 18, 24 April 2026**, 149 pages, 1066 references. Local copy: `compute/refs/radziszowski-ds1-rev18.pdf` from `https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf`. The E-JC “View PDF” URL returned HTML; the RIT file is the real 585821-byte PDF.

- Table Ia: $43\le R(5,5)\le 46$. Lower bound Exoo 1989 [Ex4]; upper bound Angeltveit–McKay [AnM4].
- Table Ib: the same upper bound 46, credited to [AnM3, AnM4].
- Item 2.1(e): McKay–Radziszowski conjecture $R(5,5)=43$ with exactly 656 critical graphs on 42 vertices; upper bound 49 (1997) then 48 (2016) then 46 (2023); no self-complementary $(5,5)$-critical graph [Chv2].
- Item 2.1(i): no Table Ia lower bound can be improved by a cyclic graph on fewer than 102 vertices, except possibly some $R(3,k)$.

Angeltveit–McKay, $R(5,5)\le 46$, arXiv:2409.15709v2 (1 September 2025). Local copy: `compute/refs/angeltveit-mckay-r55-le46.pdf`. The proof is linear programming on neighbourhood excess plus a pair of independent ~30 and ~50 CPU-year gluing censuses of dense members of $\mathcal R(4,5,n)$ for $n=21,22,23,24$. The authors write that the same method at 45 would need new theory, not more of the same computer time.

Post-April-2026 screen (arXiv + the survey itself): no later accepted movement of either endpoint.

McKay’s combinatorial-data page still hosts the 328+complements file `r55_42some.g6` (47888 bytes, SHA-256 `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`).

## What was independently verified

1. All 328 stored graphs, and all 328 complements, are $(5,5,42)$. None is self-complementary in the given labelling. Every stored graph has $\delta=19$, $\Delta=22$. Edge counts on the stored half: 423 (1), 424 (7), 425 (29), 426 (66), 427 (89), 428 (77), 429 (43), 430 (16). Script: `compute/verify_mckay.py`. Certificate: `compute/certs/mckay42_verify.json`.
2. None of the 656 graphs extends by one vertex. Neighbourhood SAT: no $K_4$ in $S$, no independent 4-set in $V\setminus S$, $18\le|S|\le 24$. 31.1s, 883980 DPLL nodes, 0 models. Script: `compute/extend_check.c`. Log: `compute/logs/extend_check.txt`. This replays McKay–Radziszowski’s extension claim. It is not a proof that $R(5,5)\le 43$.
3. Paley-17 is $(5,5)$; Paley-41 has $\omega=\alpha=5$ and is correctly rejected. Both are sanity checks of the clique code.

## What was searched and found empty

**Circulants**, legal degrees from $R(4,5)=25$. C implementation `circulant_census.c`; every HIT re-checked by `r55lib.is_ramsey`; zeros at 42 and 43 independently replayed in Python (`py_circulant.py`, 1167322 legal sets each).

- Hits exist at $n=25,29,32,33,36,37,38,40,41$ (344, 394, 384, 140, 102, 110, 18, 24, 20).
- **Zero** hits at $n=39,42,43,44,45$.
- On 43 vertices, vertex-transitive implies circulant, so there is no VT $(5,5,43)$-graph.
- None of the 20 circulant $(5,5,41)$ graphs, and none of the 24 circulant $(5,5,40)$ graphs, extends by one vertex. A non-extendable $(5,5,n)$-graph cannot sit as an induced subgraph of any $(5,5,n+k)$-graph. In particular no published 42-vertex example is “circulant-41 plus a vertex”.

**One-flip ball of the 656.** 564816 candidate flips, 4080 preserve $(5,5,42)$. Canonical 1-WL types: 194 among the 656; every surviving flip stays in those types. No new 1-WL type.

**Seidel switching.** Every 1-set and every 2-set on every one of the 656 graphs: zero $(5,5)$ results.

**Cayley graphs on all six groups of order 42**, inverse-closed connection sets, degrees in $[17,24]$. Group laws checked (`check_groups.py`). All six empty. Certificate: `compute/certs/cayley42_census.json`.

| group | leaves | hits |
|---|---:|---:|
| $C_{42}$ | 1167322 | 0 |
| $D_{21}$ | 154888897 | 0 |
| $C_7\times S_3$ | 365033 | 0 |
| $C_3\times D_7$ | 1284757 | 0 |
| $\mathrm{AGL}(1,7)$ | 949786 | 0 |
| $C_2\times F_{21}$ | 106226 | 0 |

The 656 published graphs are therefore non-Cayley. This does not rule out a non-Cayley vertex-transitive graph of order 42 (Aut without a regular subgroup), and it does not rule out a 43-vertex graph with trivial automorphism group.

**Involution-symmetric 43-vertex SAT.** Encoder validated on $n=17$: kissat SAT, decoded graph is $(5,5,17)$ with 58 edges (`certs/involution17_model.json`). The 43-vertex instances `cnf/involution43.cnf` (22785 vars) and `cnf/involution43_slim.cnf` (462 vars) both returned `s UNKNOWN` at 900s and 1200s. Those timeouts are not a dent and do not constrain involutions.

## What this is not

- Not a 43-vertex $(5,5)$-graph.
- Not a nonexistence proof at 45.
- Not a proof that the 656 graphs are all of $\mathcal R(5,5,42)$.
- Not a movement of either published endpoint.

Harborth–Krause already implied the cyclic half of the 43-census. The Cayley-on-all-groups half at 42, the independent non-extension replay, the 1-WL flip types, and the Seidel isolation are the residue.

## Replay

```
cd problems/ramsey-r55/compute
python3 verify_mckay.py
./extend_check refs/r55_42some.g6
./circulant_census 43
python3 py_circulant.py 43
python3 check_groups.py
```

## 2026-08-27 — urls opened

- `https://www.cs.rit.edu/~spr/ElJC/eline.html` — revision list still ends at #18, 24 April 2026, 149pp / 1066 refs. No #19.
- `https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf` — 585821-byte PDF, version 1.4, 149 pages. Title page “revision #18: April 24, 2026”. Table Ia: $R(5,5)$ is $43$–$46$. Item 2.1(e): conjecture $R(5,5)=43$ with exactly 656 critical graphs on 42 vertices; upper bound 46 via [AnM3]. [AnM4] in the reference list is the 2026 Journal of Graph Theory print.
- `https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1` — living DS1, `citation_firstpage` “DS1: Apr 24”, `DC.Date.modified` 2026-04-23. No later survey.
- `https://arxiv.org/abs/2409.15709` — Angeltveit–McKay v2, 1 September 2025. “The lower bound of 43 … is still the best.” 45 would need new theory.
- `https://arxiv.org/html/2409.15709v2` — same paper, HTML text used by `scripts/arxiv_fetch.py`.
- `https://export.arxiv.org/api/query?search_query=all:"R(5,5)"…&sortBy=submittedDate&sortOrder=descending` — 6 hits. Newest after 2409.15709 is 2508.16699v2.
- `https://arxiv.org/abs/2508.16699` — Tamburini, random-projector heuristic for $R(5,5)=45$. Abstract: diagnostics “identify $R(5,5)$ at $n=45$”; not a colouring and not a nonexistence log. Lead, not a bound.
- `https://users.cecs.anu.edu.au/~bdm/data/ramsey.html` — “The largest known Ramsey(5,5)-graphs”: Exoo then McKay–Radziszowski 656; “there could be more with 42 vertices and even some with 43-47 vertices.” File `r55_42some.g6` still offered.

Failed / unused: `https://www.cs.rit.edu/~spr/PUBLIC/index.html` returned 404 (the survey lives under `ElJC/`).

Independent parent replay this session: `compute/replay.sh` and `python3 verify_mckay.py`. 328+328 ok, 0 extensions, circulant 42/43 empty.

## 2026-08-27 — what q1 checked

Not a new bound. Independently verified tonight:

1. Group laws for the four groups of order 44 and both groups of order 45 (`q1/check_groups.py`).
2. No legal-degree Cayley $(5,5)$-graph on $C_2\times C_{22}$, $C_{11}\rtimes C_4$, $D_{22}$, or $C_3\times C_{15}$. Circulants at 44 and 45 empty (replay of the 17 August census). Python matched the C leaf counts on $C_{11}\rtimes C_4$ and $C_3\times C_{15}$.
3. 4080 one-flip $(5,5,42)$ neighbours of the 656; none extend (`q1/extend_flips.c`).
4. $|\mathrm{Aut}|$ of the 656 is $1$ (424 graphs) or $2$ (232 graphs); no 7-cycle.
5. No integral SRG parameters on 43 vertices with degree in $[18,24]$; $43\not\equiv 1\pmod 4$.
6. $C_7$ encoder agrees with brute force on $n=7$ and produces a $(5,5,14)$-graph. The 42- and 43-vertex slim instances timed out. Those timeouts are not a dent.

Cert: `compute/q1/certs/q1_summary.json`. Replay: `cd compute/q1 && ./run_all.sh`.

## 2026-08-29 — q3 order-7 certificates

No new Ramsey bound. The published interval remains $43\le R(5,5)\le46$.

The q2 prime-order encoder was reused unchanged. Checked certificates now
exclude all six order-7 permutation cycle counts $7^c 1^{43-7c}$ on 43
vertices. Direct DRAT proofs cover eight fixed-neighbour representatives for
$c=1,\dots,5$; complementation pairs $k$ with $c-k$. For $c=6$, a local DRUP
exhausts 787 possible 21-vertex neighbourhoods and 787 conquer DRUPs refute the
original q2 CNF under those assignments. Certificate:
`compute/q3/certs/q3_summary.json`.

By Cauchy's theorem, combining q2 and q3 leaves only 2, 3, and 5 as possible
prime divisors of the automorphism-group order of a hypothetical
$(5,5,43)$-graph. This does not rule out such a graph and does not move an
endpoint. The maximum-cycle order-2, order-3, and order-5 instances still time
out, and their other cycle types remain incomplete.

Proof-format and case-splitting references opened during the certificate work:

- `https://github.com/marijnheule/drat-trim` and
  `https://arxiv.org/abs/1610.06229` — DRAT format and the independent checker.
- `https://github.com/marijnheule/CnC` and
  `https://github.com/marijnheule/CnC/blob/master/cube-glucose-proof.sh` —
  reference cube-and-conquer implementation and incremental proof driver.
- `https://arxiv.org/abs/2209.05201` and
  `https://github.com/abhisheknair1729/Proof-Stitch` — proof combination for
  divide-and-conquer SAT. q3 keeps the 787 subproofs separate and certifies the
  finite cover, so each checker run stays small.
- `https://github.com/arminbiere/cadical` — alternate solver source inspected;
  the environment lacked a C++ compiler, so the installed PySAT CaDiCaL 1.9.5
  backend was used only for search, never as the final proof checker.

## 2026-08-29 — q4 leftover 2/3/5

No new Ramsey bound. The published interval remains $43\le R(5,5)\le46$.

Fetched again before searching:

- `https://www.cs.rit.edu/~spr/ElJC/eline.html` — revision list still ends at
  #18, 24 April 2026. No #19.
- `https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1` — living
  DS1 still dated 24 April 2026.
- `https://arxiv.org/abs/2409.15709` — Angeltveit–McKay v2. Lower bound 43 is
  still the best; 45 wants new theory.
- `https://export.arxiv.org/api/query?search_query=all:"R(5,5)"&sortBy=submittedDate&sortOrder=descending&max_results=8`
  — 6 hits. Newest after 2409.15709 is still 2508.16699v2.
- `https://arxiv.org/abs/2508.16699` — Tamburini heuristic for $R(5,5)=45$.
  Not a colouring and not a nonexistence log.
- `https://users.cecs.anu.edu.au/~bdm/data/ramsey.html` — still hosts
  `r55_42some.g6`; still says there could be more on 42–47 vertices.

q2's encoder was reused unchanged. Checked certificates now exclude the
order-5 cycle types $5^6 1^{13}$ and $5^7 1^8$ on 43 vertices (three stored
DRATs; complementation covers the paired neighbour counts). Independent
replay: `compute/q4/logs/replay_direct.txt`. The maximum-cycle order-2,
order-3, and order-5 formulas still time out, as do the other leftover
representatives that were run. This does not move an endpoint.

## 2026-08-29 — leftover SAT after 5^6 and 5^7

Fetched again before searching:

- `https://arxiv.org/abs/2409.15709` — Angeltveit–McKay v2. Lower bound 43
  is still the best; $R(5,5)\le46$; 45 wants new theory.
- `https://www.cs.rit.edu/~spr/ElJC/eline.html` — direct fetch timed out;
  the search snippet still lists revision #18, 24 April 2026, and no #19.
- `https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1` —
  living DS1 still dated 24 April 2026.
- `https://cs.rit.edu/~spr/ElJC/sur.pdf` — revision #18, 24 April 2026.

q2's encoder was reused unchanged. One new checked certificate excludes
the order-5 cycle type $5^4 1^{23}$ at $k\in\{0,4\}$ on 43 vertices
(stored as `compute/q5/certs/proofs/p5_c4_k4.drat.xz`). Independent
replay: `compute/q5/logs/replay_direct.txt`. All five maximum-cycle
formulas still time out at thirty minutes, as do the other leftover
representatives that were run. This does not move an endpoint.


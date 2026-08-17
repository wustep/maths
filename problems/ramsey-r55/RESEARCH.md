# Research note — \(R(5,5)\)

- Slug: `ramsey-r55`
- Date: 2026-08-17
- Published record (not beaten): \(43\le R(5,5)\le 46\)
- This folder: a documented search residue. No new bound.

## Published record, fetched tonight

Radziszowski, *Small Ramsey Numbers*, Electronic Journal of Combinatorics Dynamic Survey DS1, **revision 18, 24 April 2026**, 149 pages, 1066 references. Local copy: `compute/refs/radziszowski-ds1-rev18.pdf` from `https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf`. The E-JC “View PDF” URL returned HTML; the RIT file is the real 585821-byte PDF.

- Table Ia: \(43\le R(5,5)\le 46\). Lower bound Exoo 1989 [Ex4]; upper bound Angeltveit–McKay [AnM4].
- Table Ib: the same upper bound 46, credited to [AnM3, AnM4].
- Item 2.1(e): McKay–Radziszowski conjecture \(R(5,5)=43\) with exactly 656 critical graphs on 42 vertices; upper bound 49 (1997) then 48 (2016) then 46 (2023); no self-complementary \((5,5)\)-critical graph [Chv2].
- Item 2.1(i): no Table Ia lower bound can be improved by a cyclic graph on fewer than 102 vertices, except possibly some \(R(3,k)\).

Angeltveit–McKay, \(R(5,5)\le 46\), arXiv:2409.15709v2 (1 September 2025). Local copy: `compute/refs/angeltveit-mckay-r55-le46.pdf`. The proof is linear programming on neighbourhood excess plus a pair of independent ~30 and ~50 CPU-year gluing censuses of dense members of \(\mathcal R(4,5,n)\) for \(n=21,22,23,24\). The authors write that the same method at 45 would need new theory, not more of the same computer time.

Post-April-2026 screen (arXiv + the survey itself): no later accepted movement of either endpoint.

McKay’s combinatorial-data page still hosts the 328+complements file `r55_42some.g6` (47888 bytes, SHA-256 `067902e853d87b49bcef0d1d4c0e3bbadd238ee18bc65341b079a3ca4780eccb`).

## What was independently verified

1. All 328 stored graphs, and all 328 complements, are \((5,5,42)\). None is self-complementary in the given labelling. Every stored graph has \(\delta=19\), \(\Delta=22\). Edge counts on the stored half: 423 (1), 424 (7), 425 (29), 426 (66), 427 (89), 428 (77), 429 (43), 430 (16). Script: `compute/verify_mckay.py`. Certificate: `compute/certs/mckay42_verify.json`.
2. None of the 656 graphs extends by one vertex. Neighbourhood SAT: no \(K_4\) in \(S\), no independent 4-set in \(V\setminus S\), \(18\le|S|\le 24\). 31.1s, 883980 DPLL nodes, 0 models. Script: `compute/extend_check.c`. Log: `compute/logs/extend_check.txt`. This replays McKay–Radziszowski’s extension claim. It is not a proof that \(R(5,5)\le 43\).
3. Paley-17 is \((5,5)\); Paley-41 has \(\omega=\alpha=5\) and is correctly rejected. Both are sanity checks of the clique code.

## What was searched and found empty

**Circulants**, legal degrees from \(R(4,5)=25\). C implementation `circulant_census.c`; every HIT re-checked by `r55lib.is_ramsey`; zeros at 42 and 43 independently replayed in Python (`py_circulant.py`, 1167322 legal sets each).

- Hits exist at \(n=25,29,32,33,36,37,38,40,41\) (344, 394, 384, 140, 102, 110, 18, 24, 20).
- **Zero** hits at \(n=39,42,43,44,45\).
- On 43 vertices, vertex-transitive implies circulant, so there is no VT \((5,5,43)\)-graph.
- None of the 20 circulant \((5,5,41)\) graphs, and none of the 24 circulant \((5,5,40)\) graphs, extends by one vertex. A non-extendable \((5,5,n)\)-graph cannot sit as an induced subgraph of any \((5,5,n+k)\)-graph. In particular no published 42-vertex example is “circulant-41 plus a vertex”.

**One-flip ball of the 656.** 564816 candidate flips, 4080 preserve \((5,5,42)\). Canonical 1-WL types: 194 among the 656; every surviving flip stays in those types. No new 1-WL type.

**Seidel switching.** Every 1-set and every 2-set on every one of the 656 graphs: zero \((5,5)\) results.

**Cayley graphs on all six groups of order 42**, inverse-closed connection sets, degrees in \([17,24]\). Group laws checked (`check_groups.py`). All six empty. Certificate: `compute/certs/cayley42_census.json`.

| group | leaves | hits |
|---|---:|---:|
| \(C_{42}\) | 1167322 | 0 |
| \(D_{21}\) | 154888897 | 0 |
| \(C_7\times S_3\) | 365033 | 0 |
| \(C_3\times D_7\) | 1284757 | 0 |
| \(\mathrm{AGL}(1,7)\) | 949786 | 0 |
| \(C_2\times F_{21}\) | 106226 | 0 |

The 656 published graphs are therefore non-Cayley. This does not rule out a non-Cayley vertex-transitive graph of order 42 (Aut without a regular subgroup), and it does not rule out a 43-vertex graph with trivial automorphism group.

**Involution-symmetric 43-vertex SAT.** Encoder validated on \(n=17\): kissat SAT, decoded graph is \((5,5,17)\) with 58 edges (`certs/involution17_model.json`). The 43-vertex instances `cnf/involution43.cnf` (22785 vars) and `cnf/involution43_slim.cnf` (462 vars) both returned `s UNKNOWN` at 900s and 1200s. Those timeouts are not a dent and do not constrain involutions.

## What this is not

- Not a 43-vertex \((5,5)\)-graph.
- Not a nonexistence proof at 45.
- Not a proof that the 656 graphs are all of \(\mathcal R(5,5,42)\).
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

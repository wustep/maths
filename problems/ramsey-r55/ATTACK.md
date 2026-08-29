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

## 2026-08-27 — q1, after the algebraic census

House unchanged: dent = a certified 43-vertex $(5,5)$-graph, a nonexistence proof at 45 with an independently checkable log, or a documented residue. Isolated SAT timeouts are not a dent.

Fetched again, before searching:

- Radziszowski revision #18, 24 April 2026, `https://www.cs.rit.edu/~spr/ElJC/ejcram18.pdf` (149 pp, 585821 bytes). Table Ia still $43\le R(5,5)\le 46$. Item 2.1(e) still the McKay–Radziszowski conjecture $R(5,5)=43$ with 656 critical graphs; upper bound 46 via [AnM3]. [AnM4] is listed as the Journal of Graph Theory 2026 print of the same bound.
- E-JC DS1 page `https://www.combinatorics.org/ojs/index.php/eljc/article/view/DS1` still dates the living article 24 April 2026 (`DC.Date.modified` 2026-04-23). `https://www.cs.rit.edu/~spr/ElJC/eline.html` has no revision #19.
- Angeltveit–McKay arXiv:2409.15709v2, 1 September 2025. Lower bound 43 (Exoo) still the best; they write that 45 wants new theory.
- McKay combinatorial-data page still hosts `r55_42some.g6` and still says there could be more 42-vertex examples and even some on 43–47 vertices.
- arXiv API, newest `R(5,5)` hit after 2409.15709: Tamburini 2508.16699v2, a random-projector / prime-factor *heuristic* for $R(5,5)=45$. Not a colouring and not a nonexistence proof. Lead, not a citation.

Parent replay `compute/replay.sh` plus `python3 verify_mckay.py`: 328+328 ok, none extend, circulant 42/43 empty, 1-WL flip types and Seidel isolation unchanged.

q1 searches (code in `compute/q1/`):

- Group laws for $C_2\times C_{22}$, $D_{22}$, $C_{11}\rtimes C_4$, $C_3\times C_{15}$, and $C_3\times C_3\times C_5$: identity, inverses, full associativity (`q1/certs/group_laws.json`).
- Circulants at 44 and 45 replayed empty (`q1/logs/circ{44,45}.txt`), 1.70M legal connection sets each.
- Cayley, legal degrees from $R(4,5)=25$. Hits independently re-checked in Python for the two smaller groups.

| group | order | leaves | pruned | hits | sec |
|---|---:|---:|---:|---:|---:|
| $C_{44}$ (circulant) | 44 | 1704794 | — | **0** | 1.29 |
| $C_2\times C_{22}$ | 44 | 625004 | 359690 | **0** | 5.16 |
| $C_{11}\rtimes C_4$ | 44 | 294262 | 591004 | **0** | 2.77 |
| $D_{22}$ (incremental) | 44 | 469925806 | 349496800 | **0** | 406.7 |
| $C_{45}$ (circulant) | 45 | 1704794 | — | **0** | 0.95 |
| $C_3\times C_{15}$ | 45 | 93976 | 271560 | **0** | 0.92 |

Python replayed $C_{11}\rtimes C_4$ and $C_3\times C_{15}$ with the same leaf counts (`q1/certs/py_{c11c4,c3c15}.json`). There is no legal-degree undirected Cayley $(5,5)$-graph of order 44 or 45.
- No strongly regular graph on 43 vertices with degree in $[18,24]$: zero integral parameter sets, and $43\not\equiv 1\pmod 4$ so no conference graph (`q1/certs/srg43_params.json`). This excludes an SRG $(5,5,43)$-graph. It is not a bound on $R(5,5)$.
- Automorphisms of the 656: 424 have $|\mathrm{Aut}|=1$, 232 have $|\mathrm{Aut}|=2$ (an involution), none have a 7-cycle (`q1/certs/aut_mckay.json`, 0.51s, not nauty). A $C_7$-symmetric $(5,5,42)$-graph would be new.
- $C_7$ encoder: $n=7$ self-test agrees with `is_ramsey` on all 8 circulants; $n=14$ is SAT and decodes to a $(5,5,14)$-graph with 56 edges. Slim $n=42$ (123 vars) and $n=43$ (129 vars) both `UNKNOWN` at 300s. Isolated SAT timeouts are not a dent.
- One-flip then extend: 564816 candidate flips, 4080 stay $(5,5,42)$, **0 extensions** (`q1/logs/extend_flips.txt`, 183s). The published 656 do not grow by a 1-flip plus a vertex.
- Radius-2 legal 1-flips: 22000 survivors, colour-class-size histogram still only the Aut=1 / Aut=2 shapes. Not an isomorphism test.

## 2026-08-27 — result

No 43-vertex $(5,5)$-graph. No 44- or 45-vertex Cayley $(5,5)$-graph. No nonexistence proof at 45. Published record still $43\le R(5,5)\le 46$.

Documented residue, independently replayable from `compute/q1/`:

- None of the 4080 one-flip $(5,5)$ neighbours of the 656 extend.
- No legal-degree Cayley $(5,5)$-graph on any group of order 44 or 45.
- No SRG on 43 vertices in the legal degree window.
- $C_7$ SAT at 42 and 43 timed out. That is not a dent.

Do not cite this folder as a bound. Cert: `compute/q1/certs/q1_summary.json`.



## 2026-08-28 — q2

The session ended before the wrap. Interval still $43\le R(5,5)\le 46$.
No 43-vertex $(5,5)$-graph.
No nonexistence proof at 45. Residue, independently replayable from
`compute/q2/`.

- Complete two-edit ball around the 656: $656\binom{\binom{42}{2}}{2}=242870880$
  unordered toggle pairs. 11136 finish at a $(5,5,42)$-graph; none accepts a
  43rd vertex (`logs/two_edit_extend.txt`, 587s). Classification: 10864 pairs
  have two legal intermediates, 272 have one (`logs/two_edit_classify.txt`).
- Prime-order automorphism cycle types on 43 vertices, DRAT-verified UNSAT:
  $11^c1^{43-11c}$ for $c=1,2,3$; $13^c$ for $c=1,2$; $17^c$ for $c=1,2$;
  $19^c$ for $c=1,2$; $23^11^{20}$. Degree window $18\le d\le 24$ separately
  excludes $13^31^4$, $29^11^{14}$, $31^11^{12}$, $37^11^6$, $41^11^2$.
  Circulant order 43 was already empty. A hypothetical $(5,5,43)$-graph
  therefore has $|\mathrm{Aut}|$ with no prime divisor $\ge 11$. That is a
  restriction on a hypothetical graph, not a bound on $R(5,5)$.
- Local-search near graph with two bad 5-sets. Radius-6 Hamming ball is
  UNSAT by a checked DRAT (`certs/repair_r6.json`,
  `certs/proofs/repair_r6.drat.gz`). The near graph is not a Ramsey graph.
- Orders 2, 3, 5, 7: symmetry-broken SAT left `UNKNOWN`. Timeouts are not
  restrictions.

Do not cite this folder as a bound. Cert: `compute/q2/certs/q2_summary.json`.
Replay: `cd compute/q2 && ./run_all.sh`.

## 2026-08-29 — q3 order-7 leftover

House unchanged: a timeout or a restriction on a hypothetical automorphism
group is residue, not a dent. The published interval remains
$43\le R(5,5)\le46$.

Reused q2's `orbit_sat.py` without changing its encoding. The six regenerated
maximum-cycle CNFs for orders 2, 3, 5, and 7 match q2's recorded SHA-256
hashes byte for byte. Plain-CDCL five-minute reruns for the maximum-cycle
order-2, order-3, and order-5 representatives remained `UNKNOWN`.

For an order-7 permutation of type $7^c 1^{43-7c}$, choose a fixed vertex and
let $k$ count adjacent 7-cycles. The degree window $[18,24]$, complementation
($k\leftrightarrow c-k$), and relabelling of the fixed vertex reduce all
feasible values to these representatives:

| $c$ | fixed vertices | checked $k$ | result |
|---:|---:|---:|---|
| 1 | 36 | 1 | DRAT-UNSAT; covers $k=0$ by complement |
| 2 | 29 | 1, 2 | DRAT-UNSAT; covers $k=0$ by complement |
| 3 | 22 | 1, 3 | DRAT-UNSAT; covers $k=2,0$ by complement |
| 4 | 15 | 1, 2 | DRAT-UNSAT; covers $k=3$ by complement |
| 5 | 8 | 2 | DRAT-UNSAT; covers $k=3$ by complement |
| 6 | 1 | 3 | 787-case DRUP-UNSAT |

The eight direct representative proofs were independently accepted by the
pinned `drat-trim`. For $7^6 1^1$, the unique fixed vertex has degree 21 and
its three adjacent cycles induce 21 vertices with no $K_4$ and no independent
5-set. Under q2's existing symmetry breaking there are exactly 787 assignments
to the 30 edge-orbit variables in that neighbourhood. A local DRUP certifies
that enumeration as complete; 787 further DRUPs, one for each full cube, all
verify against the original q2 CNF plus the cube units. Archive and member
hashes are in `compute/q3/certs/p7_proofs.json`.

Thus no $(5,5,43)$-graph has an automorphism of order 7. With q2's exclusions
for primes at least 11, Cauchy's theorem leaves only 2, 3, and 5 as possible
prime divisors of the automorphism-group order of a hypothetical graph. This
does not move either Ramsey endpoint.

## 2026-08-29 — q3 result

No 43-vertex $(5,5)$-graph found. No nonexistence proof at 45. Published
record still $43\le R(5,5)\le46$.

Documented residue, independently replayable from `compute/q3/`:

- every order-7 automorphism cycle type on 43 vertices is certified UNSAT;
- the hypothetical automorphism-group order has prime divisors only among
  2, 3, and 5; and
- maximum-cycle order-2, order-3, and order-5 SAT remains `UNKNOWN`. Other
  cycle types for those primes remain unsearched.

Do not cite this folder as a bound. Cert: `compute/q3/certs/q3_summary.json`.
Replay: `cd compute/q3 && ./run_all.sh`.

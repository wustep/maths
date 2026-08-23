# Attack log — No-three-in-line at n=71

## 2026-08-16

- Environment created. Overnight quest. written: SAT-search 142 points on the $71\times 71$ grid, prefer
  rct4. No attack yet.

## 2026-08-16 — q1

- rct4 SAT on n=71: UNKNOWN (memory: commit 374e75b). CNF `n71-rct4.cnf` was generated but not recovered (too large; not in Add-File patches).
- Scripts recovered: `rct4_model.py`, `search_sat.py`, `search_cpsat.py`, `verify_n71.py`, `audit_dimacs.py`.

## 2026-08-16 — q2

- Continued SAT on the saved CNF; 20min UNKNOWN. Script: `long_sat_saved.py`.

## 2026-08-23 — q3: certificate shapes, ranked by cheapest first check

1. **Flammenkamp database certificate (outside this folder).** The finished
   object is the database-native rct4 code for Heule's 17 August 2026
   $n=71$ entry, a pinned decoder, the decoded 142-line coordinate file, and
   an exact replay log. It settles the case because a checked 142-set meets
   the row upper bound $D(71)\le142$. Cheapest check: fetch the single coded
   entry, decode its two column positions in each of 71 rows, and run the
   existing determinant checker. A database announcement alone is only a
   lead.
2. **Verifier gate for every claimed 142-set.** The finished object is a
   `run_all.sh` that feeds the same plain coordinate file to the committed
   Python triple-determinant checker and to a second checker in another
   language using primitive line normalization, then compares their point,
   row, and column counts. Agreement settles the computational part of any
   claimed construction; disagreement kills the claim. Cheapest check: run
   every already committed verifier before writing $D(71)=142$ anywhere.
3. **Honest `rot4` SAT — killed immediately.** The hypothetical finished
   object would be a 142-point quarter-turn-invariant coordinate file and the
   same verifier replay. It would settle $n=71$, but on an odd board every
   noncentral orbit has size four and the centre has size one, so its size is
   $0$ or $1$ modulo $4$, never $142\equiv2\pmod4$. The one-page orbit-count
   check kills this shape without a solver.
4. **Flammenkamp `rct4` SAT (the symmetry used at 65, 67, and 69).** The
   finished object is an audited DIMACS or direct CP-SAT model with the
   anti-diagonal empty, one selected half-turn pair on the main diagonal,
   35 selected four-orbits, and a decoded 142-set. It settles the case after
   the verifier gate. Cheapest check: regenerate the model, replay it first
   at $n=69$ against a published witness, and audit its orbit weights and
   DIMACS header before spending solver time at 71.
5. **Lift and perturb 69, 70, or 72.** The finished object is a 142-line
   coordinate file obtained by deleting or inserting boundary rows and
   columns in a published checked configuration, followed by a bounded local
   repair trace and the verifier replay. Any final checked file settles 71;
   the provenance does not. Cheapest check: replay the source witness, apply
   each monotone row/column map once, and count collinear triples and conflicted
   points. Kill a lift if its first image has no small repair support.
6. **`rot2` SAT, a named weaker symmetry.** The finished object is a
   half-turn-invariant 142-set, its exact encoding under 2-cycles, and the
   verifier replay. It would settle 71 while retaining more candidates than
   rct4. Cheapest check: construct the orbit/cardinality equations and solve
   small odd controls through $n=25$; proceed only if the encoding reproduces
   checked witnesses and its $n=71$ clause count fits memory.
7. **No imposed board symmetry: paired-row local search followed by SAT.**
   The finished certificate is again the plain 142-point file, with exactly
   two points in every row and column; a row-pair permutation supplies a
   compact search state, and SAT completes only the unresolved cells. It
   settles 71 only after the verifier gate. Cheapest check: seed from the
   best lifted 69/70/72 image and measure the exact number of violated maximal
   lines after one minute; abandon it if it does not beat the unperturbed
   lift.

## 2026-08-23 — q3 result

- Shape 1 ended the campaign. Flammenkamp's dated notes report that Marijn
  Heule found an rct4 solution for $n=71$ on 17 August 2026. A POST lookup of
  symmetry `c`, size 71, index 1 against the database cut of 19 August returned
  one 143-character code: one symmetry character and two columns in each of
  71 rows.
- `compute/q3/decode_database.py` decoded the pinned raw entry to
  `compute/n71-142.txt`. Re-encoding was not trusted as a geometry check.
- The previously committed `verify_n71.py` checked all 467,180 point triples
  by exact integer determinant. The independent Rust checker normalized the
  line through each of the 10,011 point pairs and found no duplicate line.
  Both checked 142 distinct points in the grid and exactly two in every row
  and column. Witness SHA-256:
  `690b7d94092a728dd0e6a2b3907ed0736e05d88c8c5a120e9735d8f9dca7b176`.
- Therefore $D(71)=142$. This is a replay of Heule's published database
  record, not a dent by this campaign. The same dated record now includes
  $n=73$, so the first current hole is $n=75$. Shapes 4–7 were not run after
  the certificate passed the verifier gate; honest `rot4` remains killed by
  the orbit-cardinality check.

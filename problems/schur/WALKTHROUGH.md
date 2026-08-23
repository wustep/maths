# Walkthrough — Improve S(7) lower bound

The 2026-08-23 pass did not find a coloring of `[1697]`, but it repaired the
experimental record: Rowley's actual `[1696]` specimen is now verified and a
new two-violation `[1697]` vector is preserved rather than described from
memory.

0. What was actually missing — a certified seven-coloring of `[1697]`.
   Rowley supplies 1696; the q1/q2 near-coloring file was empty.
1. Named false starts — the old reflection SAT, orbit min-conflicts, seed
   multipliers, and q2 CEGAR all lacked a witness. The 2026-08-23 pass did not
   rerun them.
2. The useful source recovery — the official arXiv source archive contains
   Rowley's legacy workbook. Its extracted 1,696-vector passes all 719,104
   checks and is exactly symmetric about 1697.
3. The first obstruction — appending 1697 creates 74 to 249 disjoint
   boundary conflicts, depending on its color. Any repair of that literal
   extension must therefore change at least 74 old entries.
4. The useful failure — unrestricted weighted search nevertheless reached a
   1,697-vector with only `(537,537,1074)` and `(537,640,1177)` monochromatic.
   The vector and its SHA-256 are committed under `compute/q3/`.
5. Exact repair — a lazy encoding learned 216,924 edges; a full encoding used
   all 719,952 edges and 5,076,998 clauses. Both timed out. Four local restarts
   from the near-coloring also stayed at two violations.
6. A different symmetry — reflection combined with the color involution
   `(0 1)(2 3)(4 5)(6)` avoids the elementary full-reflection contradiction,
   but its 5,045,600-clause solve also timed out.
7. Proven versus open — the Rowley specimen and the ordinary-reflection Lean
   obstruction replay. No 1,697 coloring and no unrestricted impossibility
   certificate were obtained, so the verified bound here remains
   $S(7)\geq1696$.

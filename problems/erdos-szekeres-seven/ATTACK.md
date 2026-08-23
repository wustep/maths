# Attack log — erdos-szekeres-seven

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-08-23 — backward plan

Ranked by the cost of the first decisive check.

1. **Audit a proposed 32-point construction.** Finished object: exact integer
   coordinates and a standalone verifier checking general position and every
   seven-subset. It would prove ES(7) > 32, but is a dent only if the papers do
   not already contain that lower bound. Cheapest check: read the published
   lower-bound theorem and distinguish “no seven in convex position” from
   “no empty convex heptagon.”
2. **Replay a named anchored slice from arXiv:2512.24061.** Finished object:
   the exact DIMACS instance, an UNSAT DRAT or LRAT proof, and an independent
   checker, following the ES(6) = 17 certificate pipeline. It beats the
   record only if the slice closes every case in a proved reduction. Cheapest
   check: audit the paper's coverage claim and public certificate inventory.
3. **Test a symmetry-class obstruction at 33.** Finished object: a short
   exact certificate proving that a named order-type family always contains
   a convex seven-set. This is residue unless those families exhaust every
   case. Cheapest check: enumerate toy-size orbit representatives and compare
   with direct convex-hull tests.
4. **Encode a named finite family at 33 in SAT or oriented-matroid form.**
   Finished object: DIMACS, a checked UNSAT proof, and the exact map from
   point sets to assignments. A family exclusion is residue; eliminating an
   exhaustive family moves the upper bound. Cheapest check: validate the
   chirotope and convex-seven clauses against exact small configurations.
5. **Search beyond the classical construction.** Finished object: exact
   coordinates for 33 or more points with no seven in convex position and
   two independent verifiers. A 33-point witness would prove ES(7) >= 34.
   Cheapest check: reproduce the 32-point seed before attempting mutations.
6. **Use a certificate-carrying allowable-sequence reduction.** Finished
   object: a finite state list, transition table, and independent dynamic
   program proving every terminal state contains a convex seven-set. If the
   quotient is exhaustive it could certify the 33-point upper bound;
   otherwise it is residue. Cheapest check: reproduce ES(6) at 17 with the
   same states.

## 2026-08-23 — record audit

The published record is

$$
33 \leq ES(7) \leq 113.
$$

The 1960–61 construction already gives 32 points with no convex seven-set.
Shape 1 therefore dies as a possible dent: another 32-point certificate does
not change the number. A 7-hole certificate would not address ES(7) at all.
The q1 certificate replays the correct classical construction and verifies
4,960 triples and all 3,365,856 seven-subsets independently in Python and C.

The Baek–Balko journal result does not improve the general interval. It does
show that every decomposable set with more than 32 points contains seven in
convex position, killing the decomposable construction class as a source of
a 33-point counterexample. Its abstract weak-polygon coloring at 33 is not a
point set or signotope and supplies no ES(7) lower bound.

Status: residue — the record and its lower witness were replayed, not beaten.

## 2026-08-23 — arXiv certificate audit

The cheapest named ES(7) slice in arXiv:2512.24061 has layers
`(5,5,5,5,5,5)` and offsets `(0,4,4,4,4,4)`, with a reported solve time of
2,500 seconds. The released generator makes an instance with 578,336
variables and 16,671,498 clauses after the 690 hull units are included. Its
no-convex-seven block alone contains 1,196,173,440 literals.

The public repository at commit
`9520ceac1758120124840e0b66b003c559cec4a7` contains only `README.md` and
`es_sat_gen.py`. It has no CNFs, solver versions or commands, logs, hashes,
DRAT/LRAT proofs, or checker. Two table rows do not record their offset
vectors. The anchored offset slices are also not presented as an exhaustive
or disjoint case split. The reported solver outcomes therefore cannot be
independently replayed from the published artifacts and do not yield a global
upper bound.

Status: residue — the smallest reported slice remains a lead, not a checked
certificate.

## 2026-08-23 — compact signotope encoding

Ordering a point set by x-coordinate turns every four-set into a sign sequence
with at most one change. q2 uses one orientation variable per triple and one
parity variable per four-set. Odd four-set parity is exactly the non-convex
case, so each seven-set needs one 35-literal clause. This produces 46,376
variables and 5,254,128 clauses at `(n,k)=(33,7)`.

Two independent audits exhaust the Boolean truth tables and 2,222 exact
x-ordered coordinate quadruples. Kissat returned SAT at `(8,5)` and UNSAT at
`(9,5)`; `drat-trim` independently verified the latter proof. The encoding
also returned SAT at `(16,6)`. A proof-producing `(17,6)` run was stopped
without an answer after 2 minutes 53 seconds, when its incomplete DRAT had
grown to 586,153,984 bytes.

The full 33-vertex DIMACS file has SHA-256
`3771831e7d5730d9a2ca81356253cee1c44d5744de92942f664c4767c60f58c9`
and occupies 916,030,006 bytes. Kissat 4.0.4 ran for its 300-second cap
without proof output and returned `s UNKNOWN`.

Status: residue — the finite encoding and replay path are checked, but the
full search is incomplete and the interval remains unchanged.

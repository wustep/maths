# q7 claim ledger

Status: residue at the 2026-09-12 midnight Pacific cutoff. No finite
inequality or exact value is asserted by q7.

The selected handle was to determine $m(79)$, the first prime absent from
the 20-term OEIS A398173 table opened on 2026-09-12 (UTC). The table ends
at $m(73)=16$. Its values are a source report; q7 did not replay them.
The inherited local equalities $m(59)=m(61)=15$ remain in q5 and q6.

No q7 search, witness verification, or lower exclusion ran. The q5 C and
Rust engines accept only primes below 64; widening and auditing their
masks remained undone. Thus no table extension or published improvement
was obtained. No incomplete search is offered as a lower bound.

A future exact claim requires a directly checked witness and an exhaustive,
independently checked exclusion of every smaller admissible cardinality.
A unique sum in the witness or any smaller admissible set would falsify
that future equality; an omitted branch would invalidate its exclusion.

`bash problems/unique-sum/compute/q7/run_all.sh` exits 3 immediately to
report that there is no certified q7 claim. It starts no computation.

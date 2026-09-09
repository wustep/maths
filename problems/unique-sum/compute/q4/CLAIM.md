# q4 claim ledger

Status: residue. No improvement of the published record is asserted.

The inherited certificate `../q3/p59_upper.json` gives

$$
m(59)\le15.
$$

Both the Python ordered-pair check and the independent Rust reflection check
replay this witness. OEIS A398173 now publishes m(59)=15 and exact values
through 73 (`published_oeis.json`). The local exact table still ends at 53;
a replay at 59 would match an existing record.

The target remains existence of a set of size at most 14 at 59. UNKNOWN
never excludes any size. A complete lower search must cover sizes 2 through
14, without assuming monotonicity in cardinality.

The current Rust run has completely excluded the restricted family of
sets of size at most 14 containing a five-term arithmetic progression with
nonzero difference. `p59_ap5_exact.json` records that run. The independent SAT replay
finished `UNKNOWN` after 5,000,000 conflicts in 456.150 seconds
(`sat_p59_ap5_le14.json`). It does not confirm the restricted exclusion;
no dual-check claim is made yet. The unrestricted size-at-most-14 leaf remains open.

Falsifiers: a unique unordered representation in the saved 15-set falsifies
the upper certificate. A valid set of size at most 14 containing such a
five-term progression falsifies the restricted exclusion. Any valid set
of size at most 14 settles the construction target, but its failure to
appear in a capped run does not imply a lower bound.

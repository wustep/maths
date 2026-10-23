# q7 claim ledger

Status: local exact value matching the published record at 67. No
improvement of that record is asserted. The q5 equality $m(59)=15$ and
the q6 equality $m(61)=15$ are not rewound. Draft PR #187 recorded a
cutoff before search and is not duplicated here.

The q5/q6 engines stored sets in 64-bit words. q7 widens the mask to
128 bits. The checked 16-set `p67_upper.json` and the completed
size-at-most-15 exclusion together give

$$
m(67)=16.
$$

OEIS A398173 already publishes this value (`published_oeis.json`,
retrieved 2026-09-26, revision 48). It is new to the local exact table.

The upper half is

$$
A=\{0,1,2,3,4,5,6,7,11,14,15,25,26,50,53,54\}.
$$

Python ordered-pair enumeration and the independent Rust reflection
check agree that no ordered multiplicity lies in $\{1,2\}$.

The lower half is the exact predicate

$$
\nexists A\subseteq\mathbb Z/67\mathbb Z:\quad
2\le |A|\le15,\quad A\text{ has no unique sum}.
$$

No existence monotonicity in cardinality is assumed. The argument uses
the affine normal form $\{-1,0,1\}$ and the AP-length ladder with the
128-bit C completion checker and the independent Rust unordered-pair
brancher:

- AP5: C UNSAT after 6,066,228 nodes (`p67_ap5_cover.json`); Rust UNSAT
  after 11,192,593 nodes (`p67_ap5_exact.json`).
- AP4 but not AP5: 31 named midpoint classes for center $-1=66$ on the
  AP4 root. C and Rust both return UNSAT on every representative
  (`p67_ap4_not_ap5_classes.json`, `p67_dual_ap4_not_ap5.json`).
- AP4-free: 29 named midpoint classes for center $1$ on the AP3 root.
  C and Rust both return UNSAT on every representative
  (`p67_ap4_free_classes.json`, `p67_dual_ap4_free.json`).

The published 16-sets at 71 and 73 are independently checked as upper
bounds. Dual lower replay at those primes, and the first unpublished
prime 79, remain unfinished. Matching OEIS at 67 is not a dent.

`bash compute/q7/run_all.sh` from the problem folder replays witnesses,
small exhaustive controls, partitions, stored class decisions, the q6
AP5 ceiling at 61, and one 6-point named class at 67. Full named-class
searches are the stored artifacts; they can be restarted with
`run_ladder.py`.

Falsifiers: a unique unordered representation in the saved 16-set; any
valid set of size at most 15 in $\mathbb Z/67\mathbb Z$; a SAT result
on the AP5 family or on a named-class representative recorded as UNSAT;
a missing midpoint pair or invalid affine identification in the
partition.

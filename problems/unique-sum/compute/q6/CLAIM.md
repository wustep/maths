# q6 claim ledger

Status: local exact value matching the published record. No improvement of
that record is asserted. The q5 equality $m(59)=15$ is not rewound.

The checked 15-set `p61_upper.json` and the completed size-at-most-14
exclusion together give

$$
m(61)=15.
$$

OEIS A398173 already publishes this value (`published_oeis.json`, retrieved
2026-09-09). It is new to the local exact table.

The upper half is

$$
A=\{0,1,2,3,4,6,15,21,22,24,42,49,55,56,58\}.
$$

Python ordered-pair enumeration and the independent Rust reflection check
agree that no ordered multiplicity lies in $\{1,2\}$.

The lower half is the exact predicate

$$
\nexists A\subseteq\mathbb Z/61\mathbb Z:\quad
2\le |A|\le14,\quad A\text{ has no unique sum}.
$$

No existence monotonicity in cardinality is assumed. The argument reuses
the q5 engines (C reflection cover; Rust unordered-pair brancher) with the
affine root $\{-1,0,1\}$ and the AP-length ladder:

- AP5: C UNSAT after 810,493 nodes (`p61_ap5_cover.json`); Rust UNSAT after
  1,476,025 nodes (`p61_ap5_exact.json`).
- AP4 but not AP5: 28 named midpoint classes for center $-1=60$ on the AP4
  root. C and Rust both return UNSAT on every representative
  (`ap4_not_ap5_classes.json`, `dual_ap4_not_ap5.json`).
- AP4-free: 26 named midpoint classes for center $1$ on the AP3 root.
  C and Rust both return UNSAT on every representative
  (`ap4_free_classes.json`, `dual_ap4_free.json`).

`bash compute/q6/run_all.sh` from the problem folder replays the witness,
small controls inherited from q5, stored class decisions, and the AP5
ceiling. Full named-class searches can be restarted with
`../q5/midpoint_cases.py` and `../q5/dual_classes.py`.

Falsifiers: a unique unordered representation in the saved 15-set; any
valid set of size at most 14; a SAT result on the AP5 family or on a
named-class representative recorded as UNSAT; a missing midpoint pair or
invalid affine identification in the partition.

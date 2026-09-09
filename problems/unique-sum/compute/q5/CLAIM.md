# q5 claim ledger

Status: local exact value matching the published record. No improvement of
that record is asserted.

The inherited certificate `../q3/p59_upper.json` and the completed
size-at-most-14 exclusion together give

$$
m(59)=15.
$$

OEIS A398173 already publishes this value (`published_oeis.json`, retrieved
2026-09-09). The local exact table now includes 59; it does not yet replay
61 through 73.

The upper half is the checked 15-set
$\{0,1,25,28,32,36,43,46,47,49,52,53,55,57,58\}$. Both the Python
ordered-pair check and the independent Rust reflection check replay it.

The lower half is the exact predicate

$$
\nexists A\subseteq\mathbb Z/59\mathbb Z:\quad
2\le |A|\le14,\quad A\text{ has no unique sum}.
$$

No existence monotonicity in cardinality is assumed. The argument uses the
affine normal form $\{-1,0,1\}$ and the AP-length ladder:

- AP5 (and therefore AP6): q5 Rust UNSAT after 1,559,513 nodes
  (`p59_ap5_exact.json`), matching the inherited q4 count; q5 C UNSAT after
  925,228 nodes (`p59_ap5_cover.json`). The inherited q4 CaDiCaL AP5 run is
  not rewound.
- AP4 but not AP5: 27 named midpoint classes for center $-1$ on the AP4
  root. C and Rust both return UNSAT on every representative
  (`ap4_not_ap5_classes.json`, `dual_ap4_not_ap5.json`).
- AP4-free: 25 named midpoint classes for center $1$ on the AP3 root.
  C and Rust both return UNSAT on every representative
  (`ap4_free_classes.json`, `dual_ap4_free.json`).

The 3-swap neighborhood of 31 seeds (162,932,311 fourteen-sets) found no
admissible 14-set; that search is diagnostic only.

`bash compute/q5/run_all.sh` from the problem folder replays witnesses,
small exhaustive controls, partitions, stored class decisions, and the AP5
ceiling. The full named-class searches are the stored artifacts; they can
be restarted with `midpoint_cases.py` and `dual_classes.py`.

Falsifiers: a unique unordered representation in the saved 15-set; any
valid set of size at most 14; a SAT result on the AP5 family or on a
named-class representative recorded as UNSAT; a missing midpoint pair or
invalid affine identification in the partition.

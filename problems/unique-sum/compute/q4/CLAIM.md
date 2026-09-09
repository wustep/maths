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

The unrestricted question **whether m(59) is at most 14 remains open in this
notebook**. No unrestricted lower bound at 59 is asserted. A complete lower
search must cover sizes 2 through 14, without assuming monotonicity in
cardinality.

The restricted exclusion is the exact predicate

$$
\nexists A\subseteq\mathbb Z/59\mathbb Z:\quad
2\le |A|\le14,\quad A\text{ has no unique sum},\quad
A\text{ contains a nonconstant five-term arithmetic progression}.
$$

Completed evidence:

- The 15-set upper certificate above passes Python ordered-pair enumeration
  and Rust reflection intersections.
- AP5: Rust returned UNSAT after 1,559,513 nodes
  (`p59_ap5_exact.json`). The independent CaDiCaL run also returned UNSAT
  after 14,448,284 conflicts in 1,474.911 seconds
  (`sat_p59_ap5_le14_cadical20m.json`). Its formula hash, dimensions, and
  restrictions match a fresh build of the audited encoding. There is no
  retained DRAT proof object; the lower evidence is the two completed runs
  and their reproducible implementations.
- AP6: the analogous predicate with six terms follows from AP5. It also
  has its own Rust UNSAT run, with 391,264 nodes (`p59_ap6_exact.json`).
- Midpoint partitions: all 29 nontrivial midpoint pairs are accounted for.
  For the AP3 root, center 1, and forbidden AP4, three roots are forbidden
  and 25 affine classes remain. For the AP4 root, center -1, and forbidden
  AP5, two roots are forbidden and 27 classes remain. `partition_controls.json`
  records the direct affine checks and 2,054 small-set coverage checks.
  `cover_controls.json` records 104 C-search controls against enumeration
  of 10,364 small subsets. These certify the partition and controls, **not
  exclusions of the remaining classes**. No heavy run of those classes was
  started.

Incomplete evidence:

- Unrestricted Rust: the inherited q3 prefix stopped UNKNOWN at
  100,000,000 nodes. Unrestricted q4 SAT stopped UNKNOWN at its
  three-million-conflict budget (`sat_p59_le14.json`).
- AP5 SAT: the earlier five-million-conflict run stopped UNKNOWN
  (`sat_p59_ap5_le14.json`); the later completed run supersedes that limit.
- AP4 Rust: UNKNOWN at the 600-second wall limit (`p59_ap4_exact.json`).
  No node count was emitted before termination.
- AP5 C: interrupted at the user's wrap request, exit 130, without a
  completed result (`p59_ap5_cover_interrupted.json`). It supplies no
  additional exclusion.
- The inherited one-unique-sum 14-set and radius-four search remain search
  diagnostics. The inherited probes at 79 are not an exact table extension.

The campaign stopped at the user's request. The useful leftover is the AP4
family and the 25 named AP4-free midpoint classes. The latter are conditional
on a separate AP4 exclusion; alternatively, combine AP5 with the 27 AP4-but-
AP5-free classes and those 25 AP4-free classes. None is silently treated as
UNSAT. UNKNOWN and timeout never exclude a size.

`bash compute/q4/run_all.sh` from the problem folder performs the full claim
replay, including the long AP5 SAT decision. At wrap, only the lightweight
witness, encoding, partition, and small-search checks were rerun, as requested;
the long searches were not restarted.
`wrap_checks.json` records those checks and explicitly distinguishes formula
hash verification from a new solver run.

Falsifiers: a unique unordered representation in the saved 15-set falsifies
the upper certificate. A valid set of size at most 14 containing such a
five-term progression falsifies the restricted exclusion. Any valid set
of size at most 14 settles the construction target, but its failure to
appear in a capped run does not imply a lower bound. A missing midpoint pair,
an invalid affine identification, or disagreement with exhaustive small-set
enumeration falsifies the corresponding partition or control assertion.

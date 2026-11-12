# Finite handles

The local exact replay now reaches 67 and matches OEIS A398173 at 59, 61,
and 67. OEIS continues through 73; the first absent prime is 79.

| Leaf | Required evidence | State |
| --- | --- | --- |
| Exact table at 67, 71, 73 | Witnesses and dual lower replay; compare with the published values | residue |
| Extend the exact table at 79 through 199 | Witness and dual lower replay at a prime absent from the record | open |
| Shapes of extremal sets | Affine orbit data with direct arithmetic checks; not a table extension | open |

Completed: local $m(59)=15$ (q5), local $m(61)=15$ (q6), and local
$m(67)=16$ (q7), all matching the published terms. None is a dent. At 67
the 16-set is checked in two languages; size at most 15 is excluded by
AP5 (C and Rust) together with 31 AP4-but-not-AP5 named midpoint classes
and 29 AP4-free classes, each UNSAT in C and in Rust. See `q5/CLAIM.md`,
`q6/CLAIM.md`, and `q7/CLAIM.md`.

Leftover of the 67/71/73 leaf: dual lower replay at 71 and 73. The three
published 16-sets are independently checked as upper bounds. The q7
engines use 128-bit masks, so those primes are legal inputs; the searches
were not run. The q3 replay through 53 also matches the existing record.

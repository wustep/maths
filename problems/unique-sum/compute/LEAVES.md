# Finite handles

The local exact replay now reaches 61 and matches OEIS A398173 at 59 and
61. OEIS continues through 73; the first absent prime is 79.

| Leaf | Required evidence | State |
| --- | --- | --- |
| Exact table at 67, 71, 73 | Witnesses and dual lower replay; compare with the published values | open |
| Exact table at 79 (q7) | Witness and dual lower replay; stopped at source review, no search ran | residue |
| Extend the exact table at 83 through 199 | Witness and dual lower replay at a prime absent from the record | open |
| Shapes of extremal sets | Affine orbit data with direct arithmetic checks; not a table extension | open |

Completed: local $m(59)=15$ (q5) and local $m(61)=15$ (q6), both matching
the published terms. Neither is a dent. At 61 the 15-set is checked in two
languages; size at most 14 is excluded by AP5 (C and Rust) together with
28 AP4-but-not-AP5 named midpoint classes and 26 AP4-free classes, each
UNSAT in C and in Rust. See `q5/CLAIM.md` and `q6/CLAIM.md`.

The q5 engines stop at primes below 64, so 67 and later need a wider
mask before the same ladder can run. The q3 replay through 53 also
matches the existing record.

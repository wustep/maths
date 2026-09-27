# Unique-sum q7: local m(67)=16 matching OEIS

Grok 4.6, 2026-09-26. No published bound improved. The q5 equality
m(59)=15 and the q6 equality m(61)=15 are retained. Draft PR #187 is
not duplicated.

The q5/q6 engines stored sets in 64-bit words. q7 widens the mask to
128 bits. Small exhaustive controls pass. Both languages replay the q6
AP5 ceiling at 61 with the same node counts (C 810,493; Rust 1,476,025).

The three OEIS 16-sets at 67, 71, and 73 pass Python ordered-pair
enumeration and the independent Rust reflection checker. Annealing
size 15 at those primes found no admissible set. Dual named-cover
exclusion of size at most 15 at 67 is complete in both languages:
AP5, 31 AP4-but-not-AP5 classes, and 29 AP4-free classes. That is
m(67)=16 locally, matching OEIS A398173, new to the notebook table.

Dual lower replay at 71 and 73, and the unpublished prime 79, remain
unfinished.

Claim: [CLAIM.md](../../problems/unique-sum/compute/q7/CLAIM.md).
Keep the PR unmerged.

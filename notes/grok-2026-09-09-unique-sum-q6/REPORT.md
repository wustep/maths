# Unique-sum at 61: local equality matching OEIS

Grok 4.6, 2026-09-09. No published bound improved. The q5 equality
m(59)=15 is retained.

Locally m(61)=15. The OEIS 15-set is the upper half (Python and Rust).
The lower half is a completed exclusion of every set of size at most 14:
AP5 in C and Rust, then 28 AP4-but-not-AP5 named midpoint classes and 26
AP4-free classes, each UNSAT in both languages.

Annealing size 14 and an unrestricted C search for a 15-set from
{-1,0,1} did not produce a witness. Those failures are not a lower bound.

Claim: [CLAIM.md](../../problems/unique-sum/compute/q6/CLAIM.md).
Updates the unmerged PR against main. Do not merge.

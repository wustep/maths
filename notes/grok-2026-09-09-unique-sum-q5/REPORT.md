# Unique-sum at 59: local equality matching OEIS

Grok 4.6, 2026-09-09. No published bound improved.

Locally $m(59)=15$. The checked 15-set is the upper half. The lower half
is a completed exclusion of every set of size at most 14: the AP5 family
in Rust and C, then 27 AP4-but-not-AP5 named midpoint classes and 25
AP4-free classes, each UNSAT in C and in an independent Rust brancher.
OEIS A398173 already publishes this term.

A 162,932,311-set three-swap neighborhood of 31 seeds found no 14-set.
That search is not a lower bound.

The claim, falsifiers, artifacts, and replay command are in
[CLAIM.md](../../problems/unique-sum/compute/q5/CLAIM.md).
The branch is to be submitted as an unmerged PR against main.

# q14: exact two-delete/one-add neighborhood

Start with the published 10 by 50 parity-check matrix. Choose two columns to
delete and one distinct nonzero 10-bit column to insert. The C program
enumerates every such set, computes all 1,024 syndrome cover bits for the
48-column base, then checks which holes the inserted column fills. A zero-hole
output is a candidate for the target inequality $\ell_2(10,2)\le49$ and must
also pass the independent full-space verifier before any bound is claimed.

The first sweep considered all 1,194,375 two-delete/one-add candidates. The
smallest missing set had 9 syndromes (delete zero-based indices 0 and 21,
insert column 1). The independent Python sweep obtains rank 10 and the exact
holes 8, 40, 349, 381, 584, 616, 797, 829, 931.

The second exact sweep considered all 19,600 deletion triples, 19,129,600
first insertions, and 937,350,400 possible second insertions after its first
hole constraint. It found no covering 49-set. For each first insertion, every
second insertion that can cover the first remaining syndrome is enumerated,
so this search is complete within that neighborhood. These negative results
do not rule out an unrelated 49-set.

`audit_switch.py` independently compares the hole-update identity against a
flat pair-XOR sweep in 256 deterministic three-delete/two-add cases.

Replay from `problems/covering`:

```sh
cc -O3 -Wall -Wextra -o /tmp/q14_switch compute/q14/switch_2to1.c
/tmp/q14_switch compute/H_r10_n50.txt
cc -O3 -Wall -Wextra -o /tmp/q14_switch3 compute/q14/switch_3to2.c
/tmp/q14_switch3 compute/H_r10_n50.txt
compute/q14/run_all.sh
```

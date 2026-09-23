# Covering radius 3 at redundancy 41

On 2026-09-23, q16 found a 33-block $(3,0)$-partition of the notebook's
$26\times817$ radius-3 seed by merging inherited blocks 7 and 31. An exact
search of all 561 single merges found two valid pairs. Construction QM$_4^3$
with $m=5$ gives

$$\ell_2(41,3)\le26175,$$

improving the published 26238 and the notebook's previous 26206. The
independent certificate sweeps all $2^{26}$ seed syndromes and verifies every
output-column identity. It uses the construction theorem for output coverage,
without a $2^{41}$ syndrome sweep. Replay from `problems/covering/` with
`sh compute/q16/run_all.sh`.

An exact representation count also shows that every one of the 817 seed
columns is essential for radius 3, even without partition restrictions.
This rules out a one-column deletion of this seed. The $r=24$ alternative-seed
and $r=10$ two-block handles remain open in `compute/LEAVES.md`.

Published comparison: [Davydov–Marcugini–Pambianco, Table 7.2](https://arxiv.org/html/2511.02542v1#S7.T2).

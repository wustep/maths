# Attempted bound (verification pending)

The target inequality is

$$
\ell_2(44,3)\le 52351.
$$

The prior published upper bound is 52415 in Davydov–Marcugini–Pambianco,
[arXiv:2511.02542v1, Table 7.2](https://arxiv.org/html/2511.02542v1#S7.T2).
The proposed improvement is 64 columns. This is a continuation of the
notebook's existing 817-column code, not a new small seed.

Construction: a checked 34-block (3,0)-partition of the 26 by 817 matrix,
refined to 65 blocks, supplies Construction QM₄³ (Theorem 6.1, (6.4),
(6.8)) with m=6. Its hypotheses are 817 ≥ 65 ≥ 34, and its parameters
are r=26+3·6=44 and n=64(817+1)−1=52351.

Falsifiers: a missing syndrome in the seed partition, an invalid indicator
assignment or field, an incorrect emitted column, rank below 44, or an
uncovered syndrome of the output. The output will be certified by a
construction identity and an exhaustive seed partition check, not by a
sweep of all 2^44 syndromes. No optimality claim.

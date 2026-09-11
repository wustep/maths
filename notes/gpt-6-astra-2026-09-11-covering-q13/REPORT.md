# Covering radius 3 at redundancy 44

## Result

The run certified

$$
\ell_2(44,3)\le52351,
$$

improving the 52415 upper bound in Davydov–Marcugini–Pambianco,
arXiv:2511.02542v1, Table 7.2, by 64 columns.

## Construction

The notebook's existing $26$ by $817$ radius-3 matrix is a QM₅³
construction. Its proof supplies a 34-block $(3,0)$-partition: 23 Golay
$A$-blocks, 10 blocks from the embedded 50-column radius-2 matrix, and one
W₅ block. Refining that partition to 65 blocks supplies all indicators in
$\mathbb F_{64}\cup\{*\}$ for QM₄³ with $m=6$. The resulting parameters
are

$$
r=26+3\cdot6=44,\qquad n=64(817+1)-1=52351.
$$

## Certificate

The Python builder reconstructs the 817-column parent before emitting the
partitions and output matrix. An independent C verifier:

- exhausts all 67,108,864 seed syndromes under both the 34- and 65-block
  partitions;
- checks that the latter is a refinement;
- checks $\mathbb F_2[x]/(x^6+x+1)$ and all 65 indicators;
- checks ranks, distinct nonzero columns, and all 52,351 QM₄³ column
  identities.

The syndrome bitmap is 8 MiB. The certificate uses Theorem 6.1 for the lift
and does not enumerate $2^{44}$ syndromes.

Replay from `problems/covering/`:

```sh
compute/q13/run_all.sh
```

# Certified bound

Status: certified dent (2026-09-11).

The target inequality is

$$
\ell_2(44,3)\le 52351.
$$

The prior published upper bound is 52415 in Davydov–Marcugini–Pambianco,
[arXiv:2511.02542v1, Table 7.2](https://arxiv.org/html/2511.02542v1#S7.T2).
The improvement is 64 columns. This is a continuation of the notebook's
existing 817-column code, not a new small seed.

The 34-block $(3,0)$-partition of the $26$ by $817$ seed is inherited from
its QM₅³ construction: 23 Golay $A$-blocks, the 10 blocks of the embedded
$10$ by $50$ radius-2 matrix, and one W₅ block. The committed refinement
has 65 nonempty blocks. Its block 0 receives the indicator $*$, and blocks
$1,\ldots,64$ receive the elements $0,\ldots,63$ of the field

$$
\mathbb F_{64}=\mathbb F_2[x]/(x^6+x+1).
$$

Thus Construction QM$_4^3$ (Theorem 6.1, (6.4), (6.8)) applies with $m=6$:

$$
817\ge 2^6+1=65=p(H_0,0),\qquad
r=26+3\cdot6=44,
$$

and

$$
n=2^6(817+1)-1=52351.
$$

[`verify_q13.c`](verify_q13.c) is independent of the Python builder. With one
8 MiB bitset it exhausts all $2^{26}=67{,}108{,}864$ seed syndromes under
both partitions. The 34-block partition covers 321,037 syndromes with at most
two columns and all 67,108,864 with at most three; the 65-block refinement
covers 321,067 and all 67,108,864, respectively. The same verifier checks the
field, refinement, input and output ranks, distinct nonzero columns, and every
one of the 52,351 $D_3$ or $A(h,\beta)$ output-column identities. Theorem 6.1
then certifies output covering; there is no $2^{44}$ sweep. The radius is
exactly 3 because $1+n+\binom n2<2^{44}$.

Replay from `problems/covering/`:

```sh
compute/q13/run_all.sh
```

Falsifiers: a missing syndrome in the seed partition, an invalid indicator
assignment or field, an incorrect emitted column, rank below 44, or an
uncovered syndrome of the output. No optimality claim.

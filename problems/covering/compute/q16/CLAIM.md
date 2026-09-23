# Certified bound

The exact claim is

$$
\ell_2(41,3)\le26175.
$$

The published Table 7.2 bound of Davydov–Marcugini–Pambianco,
[arXiv:2511.02542v1](https://arxiv.org/html/2511.02542v1#S7.T2), is 26238.
The notebook previously certified 26206. Thus this construction saves 63
columns against the published table and 31 against the prior notebook bound.

The seed is the certified $26\times817$ radius-3 matrix. Its inherited
34-block $(3,0)$-partition was established in q13. An exact search of all
561 unordered block pairs found two merges preserving the partition:
$(7,31)$ and $(15,24)$ (zero-based labels). The committed partition uses
$(7,31)$ and has 33 blocks. The independent C verifier sweeps all
$2^{26}=67{,}108{,}864$ seed syndromes under those labels and finds all of
them covered by at most three columns from distinct blocks.

Construction QM$_4^3$ (Theorem 6.1, (6.4), (6.8)) applies with $m=5$ since
$817\ge2^5+1=33$. The indicator set is $\mathbb F_{32}\cup\{*\}$, with
$\mathbb F_{32}=\mathbb F_2[x]/(x^5+x^2+1)$. It yields

$$
r=26+3(5)=41,\qquad n=2^5(817+1)-1=26175.
$$

The verifier checks the field, rank 41, 26,175 distinct nonzero columns,
and every $D_3$ or $A(h,\beta)$ column identity. The theorem supplies the
output covering implication; no $2^{41}$ flat sweep is claimed. The radius
is exactly 3 by the radius-2 sphere-volume bound.

Replay from `problems/covering/`:

```sh
sh compute/q16/run_all.sh
```

Falsifiers: a missing seed syndrome under the 33-block labels, invalid field
arithmetic or indicator assignment, rank below 41, a wrong output column, or
an uncovered output syndrome. No optimality claim.

# Certified radius-3 bounds

Status: certified dent (2026-09-23).

The exact target inequalities are

$$
\ell_2(41,3)\le26175,\qquad \ell_2(47,3)\le104703.
$$

Davydov–Marcugini–Pambianco,
[arXiv:2511.02542v1, Table 7.2](https://arxiv.org/html/2511.02542v1#S7.T2),
lists 26238 and 104831, respectively. The improvements are 63 and 128
columns. This notebook previously had $\ell_2(41,3)\le26206$; the first
inequality improves that by 31 columns.

The starting 26 by 817 matrix is `compute/H_R3_r26_n817.txt`. Its 34-block
$(3,0)$-partition is inherited from QM$_5^3$. Merging blocks 15 and 24
preserves coverage of all $2^{26}$ syndromes and leaves 33 blocks. Applying
Construction QM$_4^3$ (Theorem 6.1, (6.4), (6.8)) with
$\mathbb F_{32}=\mathbb F_2[x]/(x^5+x^2+1)$ gives

$$
26+3\cdot5=41,\qquad 2^5(817+1)-1=26175.
$$

For the second bound, a 129-block refinement of the inherited partition
provides all indicators in $\mathbb F_{128}\cup\{*\}$, with
$\mathbb F_{128}=\mathbb F_2[x]/(x^7+x+1)$. The same construction gives

$$
26+3\cdot7=47,\qquad 2^7(817+1)-1=104703.
$$

Run `compute/q15/run_all.sh` from `problems/covering/`. Its independent C
checkers exhaust the seed syndrome space under the 33- and 129-block
partitions, verify full rank and distinct nonzero columns, test both fields,
and compare every generated output column with the QM$_4^3$ identity. The
output syndromes are covered by Theorem 6.1; no $2^{41}$ or $2^{47}$ sweep
is claimed. The sphere-covering volume at radius two is below $2^r$ in
both cases, so the constructed codes have radius exactly three.

Falsifiers: a missing seed syndrome under either partition, a duplicate or
zero output column, rank below 41 or 47, a wrong field or indicator, an
incorrect output column, or a counterexample to the cited construction
theorem. No optimality claim.

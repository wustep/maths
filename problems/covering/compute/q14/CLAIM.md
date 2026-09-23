# Exact local exclusion; no new covering bound

Status: residue (2026-09-23).

Let $S$ be the 50-column set in `../H_r10_n50.txt`. Every 49-element set
obtained by removing two members of $S$ and inserting one nonzero vector has
at least 9 uncovered syndromes. There is no covering set obtained by removing
three members of $S$ and inserting two distinct nonzero vectors.

The exact target remains $\ell_2(10,2)\le49$. The prior certified record is
$\ell_2(10,2)\le50$ from [Wu, arXiv:2608.27494](https://arxiv.org/abs/2608.27494),
also used by [Davydov–Marcugini–Pambianco–Wu,
arXiv:2609.16078](https://arxiv.org/abs/2609.16078). The earlier published
Kaikkonen–Rosendahl construction gave 51 columns; see
[Davydov–Marcugini–Pambianco, arXiv:2511.02542, Table 5.1](https://arxiv.org/html/2511.02542v1#S5.T1).

`run_all.sh` checks the source matrix, independently recounts the best
two-delete/one-add candidate's nine holes, and reruns both complete local
searches. Exit 0 means only the restricted predicates above hold. A
two-delete/one-add candidate with fewer than nine holes, or a covering
three-delete/two-add candidate, falsifies the claim. A 49-column covering set
outside these neighborhoods would not falsify it and would establish the
still-open bound.

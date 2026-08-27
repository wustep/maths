# kissing-5d / q3

Continuation of the five-dimensional kissing-number campaign.
Search lives in `problems/kissing-5d/compute/q3/`.

Published range still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table,
Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$, Cohn–Rajagopal
arXiv:2412.00937v3). Pfender's kernel does not give an exact dual
below 44 in dim 5. The unaffiliated Zenodo $44.0297$ note is
retracted.

No unrestricted dual below 44. Numerical Delsarte is $46.3368\ldots$.
A dual allowed to be positive on $[-1,-2/3)$ is numerically $\approx 37.46$,
but that gap is not a theorem and the rational polynomials fail Sturm.

No 41-point code.

On the leftover 1480-point $(1/4)\mathbb Z^5$ graph, every extra
kisses at most 36 of the 40 $D_5$ roots. A complete scan of
$k$-supersets of actual missed-root sets, $k=4,5,6,7$, finds no
extras-clique of size $k+1$. So there is no 41-set in that graph
that uses 33 or more $D_5$-type points. The $n_1\le 32$ slice is
unfinished.

The 36-clique in the 355-point $T^5$ remainder: exact repairs of the
four published 35-cliques are empty; coloured B&B to 40 million nodes
found no 36-clique. Incomplete.

Replay: `sh problems/kissing-5d/compute/q3/run_all.sh`.

Does not claim $\tau_5=40$. The unrestricted interval did not move.

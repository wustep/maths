# kissing-5d / q4

Continuation of the five-dimensional kissing-number campaign.
Search lives in `problems/kissing-5d/compute/q4/`.

Published range still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table,
Mittelmann–Vallentin $s_{14}(5)=44.99899685\ldots$, Cohn–Rajagopal
arXiv:2412.00937v3). The unaffiliated Zenodo $44.0297$ note is
retracted.

No unrestricted dual below 44. Exact $S_k^5$ over $\mathbb Q$
(`bv.py`). Continuum Delsarte is $46.3368\ldots$. Best certified
unrestricted dual remains Levenshtein 48.

No 41-point code.

On the leftover 1480-point $(1/4)\mathbb Z^5$ graph the ten special
octads are the $D_5$ coordinate-stars. There is no 41-set that uses
24 or more $D_5$-type points (`n1_dfs_k16.json`). The $n_1\le 23$
slice is unfinished.

The 36-clique in the 355-point $T^5$ remainder: no 35-colouring;
Cadical and Glucose return no model (no stored DRAT). Share 30
through 27 with each published 35 are empty.

Replay: `sh problems/kissing-5d/compute/q4/run_all.sh`.

Does not claim $\tau_5=40$. The unrestricted interval did not move.

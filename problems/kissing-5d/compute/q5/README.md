# q5 — leftover n1 ≤ 21 and T^5 share ≤ 23

Replay:

```bash
sh compute/q5/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. The 355-point $T^5$
remainder has no 36-clique: native CaDiCaL plus `drat-trim` `s VERIFIED`
(`t5_36_proof.json`). Share 23 is empty. The 1480-graph leftover
$n_1\le 21$ with star-cover at least 4 is unfinished. No unrestricted
dual below 44 and no 41-point code.

| Script | What it does |
| --- | --- |
| `extras_types.py` | extras types on the 1480-point graph; four-seeds vs six-seeds |
| `type_a_clique.py` | 20-clique in the 160 type-A extras; missed-union size |
| `type_a_small_U.py` | leftover-tight type-A cliques; complete empty |
| `seed_graph.py` | 240-vertex seed compatibility; leftover-tight 3-star pools |
| `triple_star_extras.py` | extras SAT / B&B on each 3-star leftover pool |
| `n1_partcount.py` | HiGHS max contained-seeds for leftover $\lvert U\rvert\ge 19$ |
| `n1_leftover_sat.py` | SAT for a 41-set with $n_1\le 21$ (Cadical / Kissat) |
| `extras_clique.c` | coloured B&B for extras with $\lvert E\rvert\ge\lvert U\rvert+1$ |
| `t5_36_proof.py` | 36-clique CNF on the $T^5$ remainder; Cadical DRAT if UNSAT |
| `t5_share.c` | exact share-$s$ 36-cliques against published 35s ($s\le 23$) |
| `t5_share_pruned.py` | neighbourhood census for share 23 (prune empty $N$) |
| `dual_more.py` | further exact unrestricted dual attempts |
| `construct_more.py` | algebraic 41-point ansätze outside the leftover graphs |
| `verify.py` | replay colourings, any claimed 41-set, and dual JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

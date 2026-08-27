# q4 — leftover (1/4)Z^5 slice and T^5 36-clique

Replay:

```bash
sh compute/q4/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. This folder records
the leftover finite graphs from the previous campaign and a parallel
hunt for an exact unrestricted dual below 44 or an explicit 41-point
code. Neither endpoint moved.

| Script | What it does |
| --- | --- |
| `analyze_stars.py` | the ten octads are the $D_5$ coordinate-stars |
| `n1_le32.c` / `n1_check.py` | complete $n_1=32$ slice (C + Python) |
| `n1_complete.c` | seed-union BFS; $k\le 12$ stored in `n1_complete_k12.json` |
| `verify_n1.rs` | independent star pools, $\omega=8$ |
| `t5_omega.py` | 35-colour / SAT 36-clique of the $T^5$ remainder |
| `t5_share.c` | exact high-share 36-cliques against published 35s (28–30 empty) |
| `n1_ilp.py` | star-free seed count, HiGHS; k=4..7 empty, k≥8 cutoff |
| `bv.py` / `dual_exact.py` | exact $S_k^5$ and unrestricted dual hunt |
| `construct41.py` | algebraic 41-point ansätze outside the leftover graphs |
| `verify.py` | replay colourings, any claimed 41-set, and dual JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

# q6 — leftover n1 ≤ 21, star-cover ≥ 4

Replay:

```bash
sh compute/q6/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. q5 certified that the
355-point $T^5$ remainder has no 36-clique and emptied every 3-star
hosted leftover 41-set. This folder records the leftover $n_1\le 21$
slice of the 1480-point $(1/4)\mathbb Z^5$ graph (star-cover at least
4) and a parallel hunt for an exact unrestricted dual below 44.

| Script | What it does |
| --- | --- |
| `four_star_color.py` | greedy colouring of extras in each 4-star pool |
| `four_star_extras.c` / `.py` | leftover-tight extras B&B / SAT on each 4-star pool |
| `two_axis_extras.py` | the ten $k=28$ two-axis pools (four-seeds only) |
| `five_star_census.py` | part-count census of 5-star unions |
| `leftover_sat.py` | global SAT, $n_1\le 21$, star-cover $\ge 4$ |
| `dual_more.py` | further exact unrestricted dual attempts |
| `verify.py` | replay any claimed 41-set and dual JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

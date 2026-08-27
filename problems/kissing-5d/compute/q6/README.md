# Leftover n1 ≤ 21, star-cover ≥ 4

Replay:

```bash
sh compute/q6/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. After the $T^5$
remainder 36-clique DRAT and the 3-star leftover emptiness, this
folder records the leftover $n_1\le 21$ slice of the 1480-point
$(1/4)\mathbb Z^5$ graph and a parallel hunt for an exact
unrestricted dual below 44.

C leftover-tight branch-and-bound empties every 4-star host
(`four_star_extras.json`). A covering Python leftover-tight sample
matches (`replay_four_star.json`). A remaining 41-set in that graph
has star-cover at least 5. Global leftover SAT on that slice did
not finish. No unrestricted dual below 44.

| Script | What it does |
| --- | --- |
| `four_star_color.py` | greedy colouring of extras in each 4-star pool |
| `four_star_extras.c` / `.py` | leftover-tight extras B&B / SAT on each 4-star pool |
| `replay_four_star.py` | independent leftover-tight Python sample |
| `two_axis_extras.py` | the ten $k=28$ two-axis pools (four-seeds only) |
| `star_cover_min.py` | min $|U|$ with star-cover at least 5 |
| `five_star_color.py` / `five_star_census.py` | 5-star colouring and part-count |
| `leftover_sat.py` | global SAT, $n_1\le 21$, star-cover at least 5 |
| `leftover_global.c` | leftover-tight extras B&B with a 4-star grow-prune |
| `dual_more.py` | further exact unrestricted dual attempts |
| `verify.py` | replay any claimed 41-set and dual JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

# q4 — leftover (1/4)Z^5 slice and T^5 36-clique

Replay:

```bash
sh compute/q4/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. This folder finishes the
two leftover finite graphs from the previous campaign, and hunts in
parallel for an exact unrestricted dual below 44 or an explicit 41-point
code.

| Script | What it does |
| --- | --- |
| `color_d4.py` | 40-colour the 1480-point $(1/4)\mathbb Z^5$ graph |
| `n1_le32.c` | complete $n_1\le 32$ slices by $k$-supersets of missed sets |
| `t5_omega.py` | 35-colour the 355-point $T^5$ remainder, or SAT a 36-clique |
| `dual_exact.py` | unrestricted / 3-point dual hunt with Sturm or SOS |
| `construct41.py` | algebraic 41-point ansätze outside the leftover graphs |
| `verify.py` | replay colourings, any claimed 41-set, and dual JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

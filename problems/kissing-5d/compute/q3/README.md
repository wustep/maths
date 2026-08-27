# q3 — unrestricted dual and exact 41-point hunt

Replay:

```bash
sh compute/q3/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. This folder hunts either
an exact Gegenbauer dual that is nonpositive on the whole interval
$[-1,1/2]$ and has value $<44$, or an explicit 41-point spherical code.

| Script | What it does |
| --- | --- |
| `sphere_types.py` | extras kiss at most 36 $D_5$ roots; same-missed groups |
| `complete_slices.py` | complete $n_1\ge 33$ emptiness on the 1480-point graph |
| `union_slices.py` | generating-set scan of missed-root unions |
| `t5_repair.py` | edit-distance repairs of the published 35-cliques |
| `t5_36.py` | assembles the $T^5$ 36-clique hunt |
| `clique.c` | coloured branch-and-bound; `t5_36_c.json` is the 40M-node run |
| `a4_continuous.py` | extras over a fixed $A_4$ at height $\|s\|>2$ |
| `expand_T.py` | $T^5$ pools on larger exact angle sets |
| `golden_pool.py` | $D_5$ plus $(\varphi,1,1/\varphi,0,0)/\sqrt{2}$ |
| `dual_gap.py` | unrestricted and gapped Delsarte; Sturm certification |
| `verify.py` | replay any dual JSON under `certs/` and any claimed 41-set |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

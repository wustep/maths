# q2 — unrestricted dual hunt and exact 41-point searches

Replay:

```bash
sh compute/q2/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. This folder hunts either an
exact Gegenbauer dual that is nonpositive on the whole interval
$[-1,1/2]$ and has value $<44$, or an explicit 41-point spherical code.

| Script | What it does |
| --- | --- |
| `unrestricted_dual.py` | exact Delsarte duals forced $\le 0$ on $[-1,1/2]$ |
| `dump_t5_pool.py` | Szöllősi $T^5$ pool (360 vectors; 5 of them universal) |
| `clique41.c` | exact 41-clique search on a dumped adjacency file |
| `sphere_clique.c` | kissing graph on $(1/d)\mathbb Z^5\cap\{\lvert x\rvert^2=2\}$ |
| `layer_replace.py` | other hyperplane layer-swaps of $D_5$ and $L_5$ |
| `verify.py` | replay any dual JSON under `certs/` and any claimed 41-set |
| `t5_clique.json` | no 41-clique in the 355-point remainder (607171 nodes) |
| `sphere_d2.json` | no 41-clique on the 200-point half-integer sphere |
| `q5cap_clique.json` | no 41-clique in the 320-point $Q_5$-cap orbit |
| `t5_36_residue.json` | 36-clique hunt that would give a 41-set; incomplete |
| `sphere_d4.json` | $(1/4)\mathbb Z^5$ 41-search; incomplete |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

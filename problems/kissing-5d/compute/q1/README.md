# q1 — restricted certificates beyond the 17 August duals

Replay:

```bash
sh compute/q1/run_all.sh
```

Independent of the 17 August scripts. This folder looks for an exact dual
that excludes some $k\in\{41,42,43,44\}$ on a finite inner-product set, an
exact maximality certificate for $Q_5$ or $R_5$, or an exact spherical
code of size $>40$. A floating SDP without a positivity certificate is
an incomplete search.

| Script | Role |
| --- | --- |
| `polar_vertices.py` | vertices of the polar $\{x:\langle x,p\rangle\le 1\}$ for each 40-point code |
| `a4_containing.py` | extras over a fixed $A_4$ equator |
| `integer_restricted.py` | integer Delsarte boxes for $T_{L_5}$ and $T_{Q_5}$ |
| `restricted_duals.py` | more interpolating Gegenbauer duals |
| `szollosi_candidates.py` | discrete compatible-vector graph on known angles |
| `verify.py` | replay of any exact certificate written under `certs/` |

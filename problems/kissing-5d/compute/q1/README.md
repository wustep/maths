# q1 — polar maximality and the Q5 integer slice

Replay:

```bash
sh compute/q1/run_all.sh
```

| Script | What it certifies |
| --- | --- |
| `polar_vertices.py` / `polar.c` | polars of $D_5,L_5,Q_5,R_5$ have $\max\|x\|^2=5/4<2$ |
| `replay_max_vertex.py` | Fraction GE rebuild of each recorded vertex |
| `integer_q5_44.c` | integer $T_{Q_5}$ distributions at $N=44$ are empty |
| `dump_q5_tables.py` | C tables match Gegenbauer; $Q_5$ histogram passes |
| `check_q5_44_empty.py` | header / witness / empty-scan replay |
| `a4_containing.py` | height $\|s\|\ge 2$; discrete extras cap at 20 |
| `integer_restricted.py` | $T_{L_5}$ still has integer hits at 41, 42, 43 |
| `restricted_duals.py` | no new interpolating dual below 44 on $T_{Q_5}$ |

The unrestricted range remains $40\le\tau_5\le 44$.

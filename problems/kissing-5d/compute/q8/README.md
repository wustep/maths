# Leftover type-(0,5) five-stars and |U|=19

Replay:

```bash
sh compute/q8/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. After q7 emptied
type-$(2,1)$ and type-$(1,3)$ five-star leftover hosts, the remaining
5-star leftover hosts are the 32 type-$(0,5)$ pools ($k=30$, 625 extras).
This folder records leftover-tight SAT on that orbit representative,
and a global leftover SAT on $|U|=19$ that also forbids the two empty
five-star types.

| Script | What it does |
| --- | --- |
| `orbits.py` | Aut($D_5$) orbits; type $(0,5)$ is transitive of size 32 |
| `write_cnf.py` | leftover-tight $k=30$ and stronger global DIMACS |
| `five_star_sat.py` | native CaDiCaL / Kissat on the type-$(0,5)$ host |
| `leftover_sat.py` | global leftover SAT with type-$(2,1)$/$(1,3)$ forbids |
| `leftover_k30.c` | leftover-tight B&B on the 625 extras in that host |
| `cube_k30.py` | leftover-tight split by $\|U\|=u$ for $u=19,\ldots,30$ |
| `replay_k30.py` | independent CNF rebuild of the type-$(0,5)$ rep |
| `verify.py` | replay any claimed 41-set and search JSON |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

Native solvers (symlink to `q7/bin/`, or `sh compute/q8/setup_solvers.sh`).

# Leftover n1 ≤ 21, star-cover ≥ 5

Replay:

```bash
sh compute/q7/run_all.sh
```

The published range is still $40\le\tau_5\le 44$. After the four-star
leftover emptiness, this folder records the leftover $n_1\le 21$ slice
of the 1480-point $(1/4)\mathbb Z^5$ graph with star-cover at least 5,
and a parallel hunt for an exact unrestricted dual below 44.

Signed permutations of the coordinates act transitively on each of the
three 5-star host types (`orbits.json`). Leftover-tight SAT on a
representative, with a native CaDiCaL binary DRAT, is the certificate
for that type. Global leftover SAT on $|U|=19$ is a separate CNF.
Always-on grow prune is the leftover-tight extras branch-and-bound
change from the q6 160-candidate cap. After the type-$(2,1)$ leftover
SAT, `leftover_global` five_mode `2` also prunes grow that sits in
one of those 60 five-star unions. five_mode `3` adds the 160
type-$(1,3)$ unions after that orbit SAT.

| Script | What it does |
| --- | --- |
| `orbits.py` | Aut($D_5$) orbits of the 252 five-star hosts |
| `star_cover_min.py` | min $|U|$ with star-cover at least 5 or 6 |
| `write_cnf.py` | leftover-tight and global leftover DIMACS |
| `five_star_sat.py` | native CaDiCaL + `drat-trim` on 5-star hosts |
| `leftover_sat.py` | global leftover SAT, $|U|=19$, star-cover at least 5 |
| `leftover_global.c` | leftover-tight extras B&B; always-on grow prune |
| `replay_five_star.py` | independent CNF rebuild of the three orbit reps |
| `dual_more.py` | further exact unrestricted dual attempts |
| `verify.py` | replay any claimed 41-set and dual JSON |
| `merge_sat.py` | assemble `five_star_sat.json` / `leftover_sat.json` from native sat.json |

A numerical SDP that does not become an exact positivity certificate is
an incomplete search. The unrestricted range remains $40\le\tau_5\le 44$
unless a verifier-plus-certificate pair here says otherwise.

Native solvers (gitignored `bin/`):

```bash
sh compute/q7/setup_solvers.sh
```

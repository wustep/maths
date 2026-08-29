# Compute — five-dimensional kissing number

Replay (creates `.venv` on first run):

```bash
sh compute/run_all.sh
```

Independent certificate check only:

```bash
compute/.venv/bin/python compute/verify_certificates.py
```

| Script | What it certifies |
| --- | --- |
| `verify_configs.py` | $D_5,L_5,Q_5,R_5$ are 40-point kissing codes matching Cohn–Rajagopal Table 2.1 |
| `extend_d5.py` | $D_5$ admits no 41st point ($4/5>1/2$) |
| `levenshtein.py` | $L_5(5,1/2)=48$ |
| `d4_equator.py` | Rankin $A(4,0)\le 8$; 24-cell holes have independence number 8 |
| `q5_extend.py` | no equatorial 41st point on $Q_5$; $A_4\not\subset D_4$ |
| `certs/restricted_delsarte.json` | exact Gegenbauer duals for $T_{D_5}$ (bound 42) and $T_{L_5}$ (bound $239925/5456$) |
| `verify_certificates.py` | replays those duals from the recurrence, no other imports |
| `integer_d5.py` | integer distance distributions for $T_{D_5}$: 42, 43, 44 empty; 41 only with 20 antipodes |
| `exact_duals.py` | interpolation that *found* the duals |
| `q1/polar_vertices.py` | polars of $D_5,L_5,Q_5,R_5$ have $\max\|x\|^2=5/4<2$ |
| `q1/integer_q5_44.c` | integer $T_{Q_5}$ slice empty at $N=44$ |

The unrestricted range remains $40\le\tau_5\le 44$.

27 August continuation lives in `q1/` (polar maximality, $T_{Q_5}$ integer 44),
`q2/` (unrestricted dual hunt and exact 41-point searches), `q3/`
(leftover $(1/4)\mathbb Z^5$ / $T^5$ 36-clique handles, larger exact pools),
and `q4/` (leftover finite graphs, exact Bachoc–Vallentin
matrices over the rationals, and a parallel dual / 41-code hunt).
The unrestricted dual hunt is `q4/dual_exact.py`; nothing certified
below 44.

Later search: `sh compute/q4/run_all.sh`.
q5 leftover slices: `sh compute/q5/run_all.sh`.
The 355-point $T^5$ remainder has no 36-clique (native CaDiCaL DRAT,
`drat-trim` verified). The $n_1\le 21$ slice of the 1480-graph is
unfinished after four-star leftover emptiness
(`sh compute/q6/run_all.sh`). Later leftover search with star-cover
at least 5 lives in `q7/` (`sh compute/q7/run_all.sh`): type-$(2,1)$
and type-$(1,3)$ five-star leftover hosts are empty (native CaDiCaL
DRAT verified). The remaining type-$(0,5)$ hosts and the global
$|U|=19$ leftover SAT live in `q8/` (`sh compute/q8/run_all.sh`);
those SAT hunts did not finish (no stored verified DRAT).
The unrestricted range remains $40\le\tau_5\le 44$.

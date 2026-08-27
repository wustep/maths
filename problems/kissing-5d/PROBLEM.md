# The five-dimensional kissing number

- Slug: `kissing-5d`
- List: P30
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Discrete geometry / spherical codes
- Sources: Tao optimization-problems 29a; Boyvalenkov–Dodunekov–Musin survey
- Started: 2026-08-17

## Statement

The kissing number $\tau_5$ is between 40 and 44 and is widely expected to equal 40. No proof excludes configurations of sizes 41–44.

## Tonight

An exact dual certificate excluding some $k\in\{41,42,43,44\}$ on the whole interval $[-1,1/2]$, or a new exact 41-point spherical code in $S^4$. This is not a small-dent pass: hunt a jump of the unrestricted interval. A restricted numerical SDP that does not become an exact positivity certificate is an incomplete search. Fetch Tao $C_{29}$, Cohn, and Mittelmann–Vallentin before searching. Do not claim $\tau_5=40$ unless it is proved.

## Outcome (2026-08-17)

Published range is still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table, Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$). No unrestricted dual below 44 and no 41-point code. Restricted exact certificates are in `compute/certs/restricted_delsarte.json` and are written up in `RESEARCH.md` / `WALKTHROUGH.md`.

## Outcome (2026-08-27)

Still $40\le\tau_5\le 44$. New restricted certificates in `compute/q1/`: every published 40-point code is maximal (polar $\max|x|^2=5/4<2$), and the integer Delsarte slice of $T_{Q_5}$ is empty at $N=44$. No unrestricted dual below 44 and no 41-point code.

## Outcome (2026-08-27, continued)

Still $40\le\tau_5\le 44$. `compute/q2/` replayed the existing duals and q1 certificates, then searched for an unrestricted dual below 44 and for an exact 41-point code. Neither was found. Residue: the 36-clique hunt in the 355-point $T^5$ remainder and the 1480-point $(1/4)\mathbb Z^5$ graph did not finish.

## Outcome (2026-08-27, q3)

Still $40\le\tau_5\le 44$. No unrestricted dual below 44 and no 41-point code. On the leftover 1480-point $(1/4)\mathbb Z^5$ graph, every extra kisses at most 36 of the 40 $D_5$ roots, and a complete $U$-superset scan empties every 41-set that uses 33 or more $D_5$-type points (`compute/q3/complete_slices.json`). The $n_1\le 32$ slice of that graph, and the 36-clique in the 355-point $T^5$ remainder, remain residue.

## Outcome (2026-08-27, q4 dual)

Still $40\le\tau_5\le 44$. Exact Bachoc–Vallentin $S_k^5$ matrices over $\mathbb Q$ are in `compute/q4/bv.py`. No unrestricted dual below 44: 1-point Delsarte remains $\approx 46.34$, and every exact 3-point Putinar / p4-span / square-dictionary attempt failed to certify a value $<44$. Residue, not a dent. Replay: `python3 compute/q4/dual_exact.py`.

## Outcome (2026-08-27, q4 leftover)

Still $40\le\tau_5\le 44$. No unrestricted dual below 44 and no 41-point code. On the leftover 1480-point $(1/4)\mathbb Z^5$ graph the ten special octads are the $D_5$ coordinate-stars; there is no 41-set that uses 22 or more $D_5$-type points (`compute/q4/n1_dfs_k18.json`, `n1_dfs_k16.json`, `n1_complete_k12.json`). The $n_1\le 21$ slice of that graph remains residue. The 355-point $T^5$ remainder has no 35-colouring and no SAT 36-clique without a stored DRAT; share 24 through 30 with each published 35 are empty. Residue, not a dent. Replay: `sh compute/q4/run_all.sh`.

## Outcome (2026-08-27, q5)

Still $40\le\tau_5\le 44$. The 355-point $T^5$ remainder has no 36-clique: native CaDiCaL 3.0.1 is UNSAT and Heule `drat-trim` reports `s VERIFIED` on the binary DRAT (`compute/q5/t5_36_proof.json`). Share 23 with each published 35 is empty. On the 1480-point $(1/4)\mathbb Z^5$ graph there is no leftover 41-set whose missed-root union sits in three $D_5$ coordinate-stars. The $n_1\le 21$ slice with star-cover at least 4 remains residue. No unrestricted dual below 44 and no 41-point code. Residue, not a dent. Did not claim $\tau_5=40$. Replay: `sh compute/q5/run_all.sh`.

## Outcome (2026-08-27, q6)

Still $40\le\tau_5\le 44$. No leftover 41-set in the 1480-point $(1/4)\mathbb Z^5$ graph whose missed-root union sits in four $D_5$ coordinate-stars (`compute/q6/four_star_extras.json`, replayed in `replay_four_star.json`). The $n_1\le 21$ slice with star-cover at least 5 remains residue. No unrestricted dual below 44 and no 41-point code. Residue, not a dent. Did not claim $\tau_5=40$. Replay: `sh compute/q6/run_all.sh`.

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

An exact dual certificate excluding some $k\in\{41,42,43,44\}$, or a new exact spherical code of size $>40$ in $S^4$. A restricted numerical SDP that does not become an exact positivity certificate is an incomplete search. Fetch the current published bounds before searching.

## Outcome (2026-08-17)

Published range is still $40\le\tau_5\le 44$ (Tao $C_{29}$, Cohn table, Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$). No unrestricted dual below 44 and no 41-point code. Restricted exact certificates are in `compute/certs/restricted_delsarte.json` and are written up in `RESEARCH.md` / `WALKTHROUGH.md`.

## Outcome (2026-08-27)

Still $40\le\tau_5\le 44$. New restricted certificates in `compute/q1/`: every published 40-point code is maximal (polar $\max|x|^2=5/4<2$), and the integer Delsarte slice of $T_{Q_5}$ is empty at $N=44$. No unrestricted dual below 44 and no 41-point code.

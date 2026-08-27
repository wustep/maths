# Report — kissing-5d leftover n1 ≤ 21

Residue. Published range still $40\le\tau_5\le 44$. Did not claim
$\tau_5=40$. Did not beat Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$.

## What finished

- No leftover 41-set in the 1480-graph whose missed-root union sits
  in four $D_5$ coordinate-stars (`problems/kissing-5d/compute/q6/four_star_extras.json`,
  26.8 million leftover-tight C nodes; `replay_four_star.json` matches
  38/38). Restricted finite-graph fact, not extras $\omega$ and not
  an unrestricted bound.
- Two-axis leftover SAT: all ten $k=28$ pools SAT-unsat
  (`two_axis_extras.json`).
- Minimum $|U|$ with star-cover $\ge 5$ is 5 (`star_cover_min.json`).
  So $|U|=19$ is not empty by combinatorics.

## What did not

- No 41-point spherical code.
- No exact unrestricted dual below 44 (`dual_more.json`: 1-point
  Delsarte $\approx 46.34$; best certified ansatz this pass
  $221991/3733\approx 59.47$).
- The $n_1\le 21$ slice with star-cover $\ge 5$ is unfinished SAT /
  B&B (`leftover_sat_status.json`, `leftover_global.json` 200M nodes
  incomplete). Incomplete search is not a lower bound.

Replay: `sh problems/kissing-5d/compute/q6/run_all.sh`.

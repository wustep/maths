# Report — kissing-5d q5

Residue. Published range still $40\le\tau_5\le 44$. Did not claim
$\tau_5=40$. Did not beat Mittelmann–Vallentin $s_{14}(5)=44.998\ldots$.

## What finished

- 355-point $T^5$ remainder: no 36-clique. Native CaDiCaL 3.0.1 UNSAT;
  Heule `drat-trim` `s VERIFIED` on a 671{,}198{,}215-byte binary DRAT
  (`problems/kissing-5d/compute/q5/t5_36_proof.json`). The Szöllősi
  $T^5$ pool has no 41-point kissing code.
- Share 23 with each published 35 is empty (`t5_share23.json`).
- No leftover 41-set in the 1480-graph whose missed-root union sits
  in three $D_5$ coordinate-stars (`triple_star_extras.json`).

## What did not

- No 41-point spherical code.
- No exact unrestricted dual below 44.
- The $n_1\le 21$ slice of the 1480-graph (star-cover $\ge 4$) is
  unfinished SAT / B&B. Incomplete search is not a lower bound.

Replay: `sh problems/kissing-5d/compute/q5/run_all.sh`.
The DRAT is local (gitignored). Rebuild CaDiCaL and run
`compute/q5/t5_native_proof.sh`.

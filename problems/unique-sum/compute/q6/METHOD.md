# Named midpoint covers at 61

The q5 completion checker and Rust brancher both accept odd primes below
64, so the $p=61$ leftover is the same ladder used at 59. After excluding
every size-at-most-14 set that contains an AP5, the remaining normalized
sets either contain the AP4 root $\{-1,0,1,2\}$ and avoid AP5, or else
avoid AP4. Naming a midpoint pair for $-1$ in the first family, or for
$1$ in the second, partitions the leftover into 28 and 26 affine classes.

C computes ordered multiplicities by reflection intersections. Rust
repairs unordered unique sums. Both start from a named root and only add
vertices. A failed neighborhood or anneal is not a lower bound.

Replay, from the problem folder:

```bash
bash problems/unique-sum/compute/q6/run_all.sh
```

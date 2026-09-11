# Named midpoint covers after the AP5 ceiling

Every admissible set in $\mathbb Z/59\mathbb Z$ has an affine image
containing $\{-1,0,1\}$. q4 excluded those images that still contain a
five-term progression, through size $14$. What remains is therefore
either AP4-free, or else contains a normalized AP4 and avoids AP5.

The selected point $1$ in the AP3 root is the midpoint of one of $29$
endpoint pairs. Three of those roots already contain an AP4; the other
$26$ fall into $25$ affine classes. In the AP4 root, the selected point
$-1$ likewise has $29$ pairs; two roots contain an AP5 and the other
$27$ are distinct classes. Completing every representative, with the
matching forbidden-progression flag, covers the leftover.

The C search is the q4 completion checker with two search-order
changes that do not affect completeness: one-point repairs are tried
first, and the exact cover test of currently unique sums runs once
eight or fewer places remain (seven or fewer after the root). A
cover-node cap may skip a prune; it never records UNSAT on its own.
Memoization identifies affine-equivalent completion problems. A
separate Rust brancher, using unordered pair counts rather than
reflection intersections, is the dual on stored class roots.

Neighborhood search around the inherited near-miss and around every
$14$-subset of both checked $15$-sets is a construction probe only.
The 3-swap neighborhood of 31 seeds evaluated 162,932,311 fourteen-sets
and found none admissible. No failed neighborhood is a lower bound.

Both named families completed UNSAT in C and in Rust. Together with the
AP5 ceiling that is an unrestricted exclusion of sizes 2 through 14, so
$m(59)=15$ locally, matching OEIS A398173.

Replay, from the problem folder:

```bash
bash problems/unique-sum/compute/q5/run_all.sh
```

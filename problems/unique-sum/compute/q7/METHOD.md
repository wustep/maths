# Named midpoint covers past the 64-bit mask

The q5/q6 completion checker and Rust brancher stored sets as 64-bit
words, so they stopped at primes below 64. q7 keeps the same
completeness argument and widens the mask to 128 bits. Every odd prime
through 127 is then a legal input, including 67, 71, 73, and 79.

Any admissible set in $\mathbb Z/p\mathbb Z$ has an affine image
containing $\{-1,0,1\}$. After excluding every size-at-most-15 image
that still contains a five-term progression, the leftover is either
AP4-free, or else contains the normalized AP4 $\{-1,0,1,2\}$ and
avoids AP5.

The selected point $1$ in the AP3 root is the midpoint of one of
$(p-1)/2$ endpoint pairs. Roots that already contain an AP4 are
impossible in the AP4-free family; the others fall into affine
classes. In the AP4 root, the selected point $-1$ likewise has
$(p-1)/2$ pairs, with AP5-containing roots forbidden in that family.

The C search computes ordered multiplicities by reflection
intersections. The independent Rust brancher repairs unordered unique
sums. Both start from a named root and only add vertices. A failed
neighborhood or anneal is not a lower bound. Memo collisions evict a
state; eviction costs time, never completeness.

Replay, from the problem folder:

```bash
bash problems/unique-sum/compute/q7/run_all.sh
```

The full AP-length ladder for one prime is

```bash
python3 problems/unique-sum/compute/q7/run_ladder.py COVER EXACT P 15
```

At 67 that ladder is stored and dual-complete. Dual lower replay at 71
and 73 is the leftover of this leaf.

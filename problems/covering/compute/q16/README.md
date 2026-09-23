# q16: covering exploration

Started 2026-09-23. Three finite handles, each outside the settled q9–q12
searches:

1. **Inherited partition merge, $r=41$, radius 3.** The q13 817-column seed
   has a certified 34-block $(3,0)$-partition. Merging any two blocks gives
   33, the field-size threshold for QM$_4^3$ with $m=5$. This would give
   $n=32(817+1)-1=26175$, shorter than the notebook's 26206 and the
   published 26238. Test all 561 unordered merges using exact counts of
   distinct-block three-column representations. This is the first handle.
2. **New small radius-3 seed at $r=12$.** q12 excluded $p\le17$ only for the
   specific OK37 matrix. A different $n\le37$ radius-3 seed with such a
   partition would permit QM$_4^3$ at $m=4$ and $r=24$. This requires a
   matrix search, not a repeat of q12's fixed-matrix SAT proof.
3. **Two quotient-block replacement at $r=10$.** q9 replaced one block and
   left 49 open. Simultaneously changing two blocks is a distinct move; its
   feasibility depends on a constrained pair-cover search, rather than a
   deletion or one-block repair.

The first handle is the smallest exact finite test and has a 31-column prize.

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

## Outcome

The exact merge sweep tested all 561 pairs. Two preserve the $(3,0)$
partition: (7,31) and (15,24). The first is committed as
[`partition_r26_n817_p33.txt`](partition_r26_n817_p33.txt). The independent
full seed sweep and lift identity check prove the inequality in
[`CLAIM.md`](CLAIM.md). Replay with `sh compute/q16/run_all.sh` from the problem
folder.

A follow-up exact deletion screen counts every representation by at most
three distinct seed columns. Every one of the 817 columns participates in a
unique representation of at least one syndrome. This holds with the 33-block
restriction (59,867,904 uniquely represented syndromes) and without it
(59,734,976). Thus no one-column deletion of this particular seed can retain
radius 3, even if the partition is discarded. This does not exclude a
different 816-column matrix.

The search code is [`search_merges.c`](search_merges.c); run it from the
repository root after compiling with `cc -O3 -std=c11` and pass the 817-column
seed and q13 34-block partition. The scan is exact and uses about 600 MiB.

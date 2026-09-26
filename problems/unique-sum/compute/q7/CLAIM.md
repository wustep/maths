# q7 claim ledger

Status: in progress. The q5 equality $m(59)=15$ and the q6 equality
$m(61)=15$ are not rewound. Draft PR #187 recorded a cutoff before
search at 79 and is not duplicated here.

The q5/q6 engines stored sets in 64-bit words. q7 widens the mask to
128 bits and runs the same AP-length ladder at the next published
primes. OEIS A398173 already publishes $m(67)=m(71)=m(73)=16$
(`published_oeis.json`, retrieved 2026-09-26, revision 48). Matching
those terms is a local table extension, not an improvement of the
record. The first prime absent from the published table remains 79.

The upper half, independently checked by Python ordered-pair
enumeration and by the Rust reflection checker, is

$$
\begin{aligned}
A_{67}&=\{0,1,2,3,4,5,6,7,11,14,15,25,26,50,53,54\},\\
A_{71}&=\{0,1,2,3,4,5,7,8,12,31,45,46,57,59,61,64\},\\
A_{73}&=\{0,1,2,3,4,5,8,9,13,21,23,25,29,44,45,65\}.
\end{aligned}
$$

The lower half is the exact predicate, for each of those primes $p$,

$$
\nexists A\subseteq\mathbb Z/p\mathbb Z:\quad
2\le |A|\le15,\quad A\text{ has no unique sum}.
$$

No existence monotonicity in cardinality is assumed. The argument uses
the affine normal form $\{-1,0,1\}$ and the AP-length ladder with the
128-bit C completion checker and the independent Rust unordered-pair
brancher.

A completed local equality matching OEIS is not a dent. A dent would
be a checked 15-set at one of these primes, or an exact value at a
prime absent from the published table (first: 79).

`bash compute/q7/run_all.sh` from the problem folder replays the
witnesses, small exhaustive controls, and partitions. Full named-class
searches are stored artifacts; they can be restarted with
`run_ladder.py`.

Falsifiers: a unique unordered representation in a saved 16-set; any
valid set of size at most 15; a SAT result on the AP5 family or on a
named-class representative recorded as UNSAT; a missing midpoint pair
or invalid affine identification in the partition.

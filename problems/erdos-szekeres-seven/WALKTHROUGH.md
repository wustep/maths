# Walkthrough — erdos-szekeres-seven

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.

## 0. What was actually missing

The first missing item was not a clever configuration. It was a trustworthy
baseline. Several nearby statements use the number 33, but they refer to
different objects: arbitrary point sets, decomposable sets, signotopes, or
abstract colorings. Only the first defines ES(7).

Reading the lower and upper sources fixes the interval at

$$
33 \leq ES(7) \leq 113.
$$

The notebook therefore needed either a 33-point counterexample, a complete
upper-bound certificate, or an honest account of why a finite computation
had not supplied one.

## 1. Named false starts

The first false start was a 32-point witness. Such a witness is worth
replaying, but the classical construction already has that size. The second
was the phrase “no 7-hole”: emptiness is not part of the definition of
ES(7). The third was to read the journal paper's weak-polygon coloring as a
geometric construction. It is an abstract hypergraph coloring, not a point
set. The fourth was to treat a table of anchored SAT slices as an exhaustive
case split. The paper makes no such coverage argument.

## 2. The useful failure

The public SAT repository has a generator but no large CNF, solver log,
proof trace, hash, or checker. That changed the target. Repeating a printed
`UNSAT` line would not be a replay; the finished object has to include a
proof that a second program accepts.

Proof production itself became the useful warning. At the ES(6) boundary,
the compact signotope encoding had already written 586,153,984 bytes of an
incomplete DRAT trace after 2 minutes 53 seconds. It still had no answer.
This made an unbudgeted proof run at 33 indefensible.

## 3. The click

Label the points by increasing x-coordinate. For four labels
`a < b < c < d`, examine the orientations of `abc`, `abd`, `acd`, and
`bcd`. A realizable point set has at most one sign change in this sequence.
That is the local signotope rule, and it needs only eight forbidden truth
table rows.

The parity of those four signs supplies the other compression. Odd parity
means that one point lies inside the triangle of the other three. Thus one
Boolean variable can record whether a four-set blocks convexity, replacing
the paper's fourteen pattern selectors.

## 4. The argument

Every geometric counterexample can first be ordered by x-coordinate. Its
triple orientations then satisfy every local signotope clause. For each
four-set, the parity clauses make the auxiliary variable true exactly in the
non-convex case. Finally, a seven-set is not in convex position exactly when
at least one of its 35 four-subsets is non-convex.

Consequently every 33-point counterexample gives a satisfying assignment to
the q2 formula. An independently checked UNSAT proof for that formula would
therefore prove that no geometric counterexample exists. The converse is not
available: a satisfying signotope need not be realizable by straight-line
points.

## 5. Computer search

The lower-bound replay generated the classical 32 points from the published
recurrence. A Python verifier found 12,740 non-convex four-set blockers and
used them to check all 3,365,856 seven-subsets. An independent C verifier
enumerated the same seven-subsets by convex-hull size and found none of size
seven.

For the signotope encoding, exact audits checked all 16 parity rows, all
eight allowed local sign sequences, and 2,222 coordinate quadruples. The
small SAT boundary was `(8,5)` SAT and `(9,5)` UNSAT, with the latter DRAT
proof accepted by `drat-trim`. The full `(33,7)` formula was generated and
hashed, then returned `s UNKNOWN` after a bounded 300-second run.

## 6. Proven versus still open

The notebook independently replays the known lower witness and the arithmetic
behind both published endpoints. It also supplies a smaller, deterministic
33-vertex relaxation whose certificate plumbing works at a toy boundary.

It does not improve either endpoint. The full signotope instance is
unresolved, the arXiv anchored runs lack public proof artifacts, and ES(7)
remains open.

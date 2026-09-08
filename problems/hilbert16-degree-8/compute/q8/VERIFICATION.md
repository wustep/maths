# What the two checks establish

A certificate supplies all 45 lattice points, 64 primitive triangles,
integer heights, and 45 signs. A strict lower lifting is essential:
only then does combinatorial patchworking give an algebraic curve.

The Python check uses `tcurve.py`. It solves each triangle's affine
height plane with rational arithmetic and tests all other lattice
points against that plane. It traces the curve segments and connects
the complementary triangle pieces in the projective plane and its
double cover, then builds the oval nesting forest.

The Rust check reads the raw point/triangle data, without importing
Python's prepared complex. Barycentric determinants test every strict
lower-face inequality using checked integer arithmetic. Distinct
primitive lower facets have disjoint interiors, and 64 such facets
have the whole area of the degree-eight triangle. This also rules
out gaps and overlapping cells.

For topology, Rust reflects the vertices and edges into the four
quadrants and follows monochromatic edges. Within each triangle,
the part of a complementary region is connected to its vertices;
when two vertices belong to that part, their edge is monochromatic.
Thus the graph components are precisely the complementary regions.
Filling monochromatic triangles changes neither these components
nor whether they contain an orientation-reversing loop.

An edge identifying antipodal boundary vertices receives parity one;
ordinary edges receive parity zero. A graph traversal propagates
these parities. A contradictory cycle detects the unique
nonorientable outside region in the projective plane. Bichromatic
edges give adjacency between the regions. Since the degree is even,
the curve has only ovals, each separating a disk from its exterior.
Their adjacency is a tree rooted at the outside region. The verifier
checks that it is a connected tree and encodes it recursively.
Its nonroot vertices correspond to the ovals, with the same nesting
order as the Python forest.

Both implementations must report the same full tree, the claimed
tree must match it, and that tree must be nonempty and absent from
both parts of the baseline. An isomorphic tree is encoded by sorting
the child encodings and enclosing their concatenation in a pair of
balanced bits. These encodings are exact, not hashes; at 22 ovals
the encoding has 46 bits.

`controls.py --full-baseline` checks all published certificates and
the seventeen additions with both implementations. Default controls
check the 55 seeds, reject known schemes and a falsely claimed open
nest, and damage signs, heights, points and triangles. The Rust
negative controls run directly, so a Python rejection cannot mask a
missing Rust check. A forced-discovery control removes a known
answer from the search filter and requires its exact witness to be
emitted. A radius-two trace on a changed mesh is compared with an
independently enumerated set of sign masks and Python topologies.

Coverage is separate. `replay_coverage.sh` audits the saved manifest;
`replay_coverage.sh --replay` reruns every sign ball and compares all
frequencies. Neither command certifies a new scheme. `run_all.sh`
returns zero only after the existence predicate in `CLAIM.md` passes.

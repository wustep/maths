# What the two checks establish

The geometry and topology checks are the same pair as in
[`../q8/VERIFICATION.md`](../q8/VERIFICATION.md). A certificate
supplies all 45 lattice points, 64 primitive triangles, integer
heights, and 45 signs. Python traces curve segments in the
projective plane and its double cover. Rust reconstructs
monochromatic regions from barycentric determinants and a vertex
graph. Both must recover the same nesting tree, the claimed tree
must match it, and that tree must be nonempty and absent from the
2,367 published schemes, the seventeen parent additions, and the
q8 scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩.

`controls.py --full-baseline` checks all published certificates,
the seventeen additions and the q8 scheme with both implementations.
Default controls check the 55 seeds and the q8 scheme, reject those
known schemes and a falsely claimed open nest, and damage signs,
heights, points and triangles. A forced-discovery control and a
radius-two Python/C trace of 1,036 sign masks are unchanged from q8.

Coverage of the remaining 1,108 balls is separate.
`collect.py` merges shard manifests into a compact summary.
`coverage.py` audits that summary against the q8 plan. Neither
command certifies a new scheme. `run_all.sh` returns zero only after
the existence predicate in `CLAIM.md` passes.

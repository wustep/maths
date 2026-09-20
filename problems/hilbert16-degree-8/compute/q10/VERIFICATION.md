# What the two checks establish

The geometry and topology checks are the same pair as in
[`../q8/VERIFICATION.md`](../q8/VERIFICATION.md). A certificate
supplies all 45 lattice points, 64 primitive triangles, integer
heights, and 45 signs. Python traces curve segments in the
projective plane and its double cover. Rust reconstructs
monochromatic regions from barycentric determinants and a vertex
graph. Both must recover the same nesting tree, the claimed tree
must match it, and that tree must be nonempty and absent from the
2,367 published schemes, the seventeen parent additions, the q8
scheme ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, and the nine q9 schemes.

`controls.py --full-baseline` checks all published certificates,
the seventeen additions, the q8 scheme and the nine q9 schemes with
both implementations. Default controls check the 55 seeds, q8 and
q9, reject those known schemes and a falsely claimed open nest, and
damage signs, heights, points and triangles. A forced-discovery
control and a radius-two Python/C trace of 1,036 sign masks are
unchanged from q8.

Coverage of the 106 leftover balls is separate.
`collect.py` merges shard manifests into a compact summary.
`coverage.py` audits that summary against the leftover plan. Neither
command certifies a new scheme. `run_all.sh` returns zero only after
the existence predicate in `CLAIM.md` passes.

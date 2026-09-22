# Eight more degree-eight T-curve schemes

**Number of nonempty degree-eight T-curve schemes ≥ 2,415.**
Eight schemes lie outside the 2,407 baseline formed by the 2,367
certificates of Geiselmann et al., arXiv:2602.06888v4, the
notebook's seventeen prior additions, the q8 scheme
⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, the nine q9 schemes, and the thirteen q10
schemes:

- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (18 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (19 ovals)
- ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (16 ovals)
- ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (16 ovals)
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩ (19 ovals)
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨10⟩⟩ (19 ovals)
- ⟨1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (17 ovals)
- ⟨1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨10⟩⟩ (17 ovals)

Neither of the two open maximal deep nests is decided.

The [claim](CLAIM.md) is the existence of these eight certificates.
From the repository root, replay with:

```sh
sh problems/hilbert16-degree-8/compute/q11/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. It runs positive and negative controls, checks each
integer lifting, independently computes the nesting tree in Python
and Rust, and checks absence from the 2,407-scheme baseline. Exit
zero means the claim holds.

The 205 leftover one-flip balls of the seven q10 followup certificates
all finished: 3,121,330 evaluations, five of the eight schemes.
One-flip balls of those five certificates then produced the other
three (150 balls, 2,283,900 evaluations).

```sh
python3 problems/hilbert16-degree-8/compute/q11/collect.py
python3 problems/hilbert16-degree-8/compute/q11/coverage.py
```

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary for verification.

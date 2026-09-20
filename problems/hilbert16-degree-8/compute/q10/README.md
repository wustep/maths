# Thirteen more degree-eight T-curve schemes

**Number of nonempty degree-eight T-curve schemes ≥ 2,407.**
Thirteen schemes lie outside the 2,394 baseline formed by the 2,367
certificates of Geiselmann et al., arXiv:2602.06888v4, the
notebook's seventeen prior additions, the q8 scheme
⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, and the nine q9 schemes:

- ⟨1 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (16 ovals)
- ⟨2 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (17 ovals)
- ⟨3 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (18 ovals)
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (17 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (19 ovals)
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (20 ovals)
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (17 ovals)
- ⟨1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (15 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (18 ovals)
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨10⟩⟩ (19 ovals)
- ⟨4 ⊔ 2⟨1⟩ ⊔ 1⟨10⟩⟩ (19 ovals)
- ⟨1 ⊔ 1⟨1⟩ ⊔ 1⟨4⟩ ⊔ 1⟨9⟩⟩ (18 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨5⟩ ⊔ 1⟨9⟩⟩ (20 ovals)

Neither of the two open maximal deep nests is decided.

The [claim](CLAIM.md) is the existence of these thirteen certificates.
From the repository root, replay with:

```sh
sh problems/hilbert16-degree-8/compute/q10/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. It runs positive and negative controls, checks each
integer lifting, independently computes the nesting tree in Python
and Rust, and checks absence from the 2,394-scheme baseline. Exit
zero means the claim holds.

The 106 leftover one-flip balls of the four q9 followup certificates
all finished: 1,613,956 evaluations, six of the thirteen schemes.
One-flip balls of those six certificates then produced the other
seven (169 balls, 2,573,194 evaluations).

```sh
python3 problems/hilbert16-degree-8/compute/q10/collect.py
python3 problems/hilbert16-degree-8/compute/q10/coverage.py
```

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary for verification.

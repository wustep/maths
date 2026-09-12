# Nine more degree-eight T-curve schemes

**Number of nonempty degree-eight T-curve schemes ≥ 2,394.**
Nine schemes lie outside the 2,385 baseline formed by the 2,367
certificates of Geiselmann et al., arXiv:2602.06888v4, the
notebook's seventeen prior additions, and the q8 scheme
⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩:

- ⟨3 ⊔ 1⟨5⟩ ⊔ 1⟨10⟩⟩ (20 ovals)
- ⟨5 ⊔ 1⟨2⟩ ⊔ 1⟨3⟩ ⊔ 1⟨7⟩⟩ (20 ovals)
- ⟨5 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (20 ovals)
- ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (19 ovals)
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (18 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨2⟩ ⊔ 1⟨9⟩⟩ (17 ovals)
- ⟨4 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (20 ovals)
- ⟨3 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (19 ovals)
- ⟨2 ⊔ 1⟨1⟩ ⊔ 1⟨3⟩ ⊔ 1⟨9⟩⟩ (18 ovals)

Neither of the two open maximal deep nests is decided.

The [claim](CLAIM.md) is the existence of these nine certificates.
From the repository root, replay with:

```sh
sh problems/hilbert16-degree-8/compute/q9/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. It runs positive and negative controls, checks each
integer lifting, independently computes the nesting tree in Python
and Rust, and checks absence from the 2,385-scheme baseline. Exit
zero means the claim holds.

The remaining 1,108 balls of the q8 one-flip radius-three plan all
finished: 16,870,408 evaluations, five of the nine schemes. One-flip
balls of those five certificates then produced the other four
(115 balls, 1,750,990 evaluations). One-flip balls of the q8
certificate itself (21 balls, 319,746 evaluations) added nothing.
The published (19,3) M-certificate neighbourhood in the leftover
plan (123 balls) hit neither open nest.

```sh
python3 problems/hilbert16-degree-8/compute/q9/collect.py
python3 problems/hilbert16-degree-8/compute/q9/coverage.py
```

`lift_candidate.py` can repeat a lifting solve with SciPy; those
packages are unnecessary for verification.

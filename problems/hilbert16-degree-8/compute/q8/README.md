# One more degree-eight T-curve scheme

**Number of nonempty degree-eight T-curve schemes ≥ 2,385.**
The new scheme is **⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩**: three exterior ovals,
one oval containing three ovals, and another containing twelve.
It has twenty ovals. Neither of the two open maximal deep nests
is decided.

The [claim](CLAIM.md) improves the 2,384 baseline consisting of
the 2,367 certificates of [Geiselmann et al., v4, §4.3](https://arxiv.org/pdf/2602.06888v4)
and the notebook's seventeen prior additions. The original archive
and those seventeen certificates remain the comparison baseline.

From the repository root, replay the new construction with:

```sh
sh problems/hilbert16-degree-8/compute/q8/run_all.sh
```

This needs Python 3, a C compiler and `rustc`, with no Python packages
to install. It runs positive and negative controls, checks the
integer lifting, independently computes the nesting tree in Python
and Rust, and checks absence from both baseline sets. Exit zero
means the claim holds. A missing or empty certificate is a failure.

The [certificate](certs/new_schemes.json) contains all triangles,
heights and signs. [VERIFICATION.md](VERIFICATION.md) explains why
the two algorithms determine the same mathematical object without
sharing the search engine. To repeat the full baseline comparison:

```sh
python3 problems/hilbert16-degree-8/compute/q8/controls.py --full-baseline
```

The search changed one diagonal and at most three signs from each
seed. It stopped at the first candidate, after 82 of 1,190 planned
balls, and then certified that candidate. The saved prefix has
1,248,532 evaluations, counting repetitions between balls. There
are 807 distinct observed schemes. Of these, 806 are in the baseline
and one is new; the remaining 1,108 balls were not searched.

```sh
# Audit the saved prefix, including every flip and all counts:
sh problems/hilbert16-degree-8/compute/q8/replay_coverage.sh
# Recompute that prefix and compare every scheme frequency:
sh problems/hilbert16-degree-8/compute/q8/replay_coverage.sh --replay
```

These commands check search coverage separately from the existence
claim. The [route notes](ROUTES.md) give the exact change from the
published seed and record the failed projection method before the
successful lifting solve. `lift_candidate.py` can repeat that solve
with NumPy and SciPy; those packages are unnecessary for verification.
The search uses one worker and bounded sign balls, with an atomic
checkpoint after each ball.

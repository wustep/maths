# A new degree-eight T-curve scheme

**Number of nonempty degree-eight T-curve schemes ≥ 2,385.**
The new scheme is ⟨3 ⊔ 1⟨3⟩ ⊔ 1⟨12⟩⟩, with twenty ovals.
It improves the notebook's 2,384 baseline by one and the 2,367
schemes in Geiselmann et al., arXiv:2602.06888v4, by eighteen in
total. Neither preferred maximal deep nest is decided.

The interrupted session left a claim, route notes and two source
files, but no completed search output. GPT-6 Astra resumed that
work, replayed the published archive and seventeen prior additions,
and completed the search driver and its independent Rust verifier.
The search stopped on its first candidate after 82 of 1,190 planned
balls, 1,248,532 sign evaluations. There were 807 observed schemes;
only one was outside the baseline.

The old lifting did not support the flipped mesh. A projection
method also failed to obtain a lifting. A linear feasibility solve
then found integer heights, and exact arithmetic verified every
strict inequality with minimum slack 4. This is a useful example
of why a failed numerical search is not a nonexistence result.

Validation completed:

- The parent replay passes all published certificates, the seventeen
  additions, and its existing controls.
- Python and Rust independently verify all 2,384 baseline schemes
  and the new certificate.
- Positive, rejection and forced-discovery controls pass, including
  1,036 independently enumerated sign assignments on a flipped mesh.
- `q8/run_all.sh` exits zero for the new certificate.
- A fresh replay reproduces every frequency in all 82 saved balls.
- Repeating the optional lifting solve reproduces the exact
  committed certificate.

The construction, claim, verifiers and retained search prefix live in
[`compute/q8`](../../problems/hilbert16-degree-8/compute/q8).
Replay requires Python, a C compiler and `rustc`; numerical packages
are needed only to repeat the optional lifting search. The hunt used
one worker; the discovery run's peak resident memory, including its
compiler child, was 45,552 KiB. Search stopped on certification,
leaving 1,108 balls unsearched. Covering was not changed.

The PR is to remain unmerged.

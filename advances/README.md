# Ten advances (context catalog)

Source announcement (1 August 2026):
[Ten advances in mathematics and theoretical computer science](https://openai.com/index/ten-advances-in-mathematics/)
(OpenAI).

Supporting material OpenAI published alongside the post:

- Paper: <https://cdn.openai.com/pdf/ten-proofs-oai.pdf>
- Reasoning walkthroughs: <https://cdn.openai.com/pdf/reasoning-walkthroughs.pdf>
- Lean 4 certificates: <https://github.com/openai/ten-proofs>

This folder is a **pointer catalog**, not a copy of those manuscripts and not
an endorsement that the claims have completed journal peer review. OpenAI
describes the Lean files as agent-reviewed certificates (`sorry` count
reported as zero in their manifest). Treat each item as a research claim
with a public formalization to inspect.

The ten results, as listed by OpenAI / `ten-proofs`:

1. **High-dimensional sphere packing.** Improved asymptotic upper bounds on
   sphere-packing density, reaching the Cohn–Elkies threshold. OpenAI
   describes this as the first improvement to the general packing exponent
   since 1978 (about 0.5991 → 0.6044) and as showing the Cohn–Elkies linear
   program cannot beat the new exponent.
   Lean: [`SpherePacking.lean`](https://github.com/openai/ten-proofs/blob/main/SpherePacking.lean)

2. **Binary and spherical codes.** Exponentially stronger upper bounds on
   the size of binary codes at any prescribed minimum distance, with
   analogous results for high-dimensional spherical codes.
   Lean: [`MetricCodes.lean`](https://github.com/openai/ten-proofs/blob/main/MetricCodes.lean)

3. **Non-sofic groups.** An explicit construction of a non-sofic group,
   addressing whether every group admits finite permutation approximations
   (soficity, after Gromov / Weiss).
   Lean: [`NonSoficGroup.lean`](https://github.com/openai/ten-proofs/blob/main/NonSoficGroup.lean)

4. **Connes’s rigidity conjecture.** A counterexample to the conjecture
   that certain groups are uniquely determined by their group von Neumann
   algebras. Concurrent independent work toward a counterexample has also
   been reported.
   Lean: [`ConnesRigidity.lean`](https://github.com/openai/ten-proofs/blob/main/ConnesRigidity.lean)

5. **Arithmetic circuit complexity.** New lower bounds for computing the
   permanent with arithmetic circuits and formulas, including an
   \(n^4 / \log n\) formula lower bound. This is a lower-bound advance
   inside those models; it is not a resolution of VP vs VNP.
   Lean: [`Permanent.lean`](https://github.com/openai/ten-proofs/blob/main/Permanent.lean)

6. **Quantum parallel repetition.** Exponential parallel repetition for
   every finite two-player entangled (quantum) game — soundness
   amplification when players must win every copy.
   Lean: [`QuantumParallelRepetition.lean`](https://github.com/openai/ten-proofs/blob/main/QuantumParallelRepetition.lean)

7. **Closest vector problem.** Polynomial-factor hardness of approximation
   for Euclidean CVP (OpenAI states a deterministic 3SAT reduction giving
   NP-hardness within \(n^{1/400}\)), with related claims for
   nearest-codeword / syndrome decoding and \(\ell_p\) CVP. This is
   worst-case hardness, not an attack on deployed lattice cryptography.
   Lean: [`GapCVP.lean`](https://github.com/openai/ten-proofs/blob/main/GapCVP.lean)

8. **Ehrhart’s volume conjecture.** The sharp maximum volume
   \((n+1)^n / n!\) in every dimension for a convex body whose centroid
   (barycenter) is its only interior lattice point.
   Lean: [`EhrhartVolumeInequality.lean`](https://github.com/openai/ten-proofs/blob/main/EhrhartVolumeInequality.lean)

9. **Multicolor Ramsey numbers.** A superexponential lower bound for
   multicolor triangle Ramsey numbers, claimed as \(R_k(3) = k^{\Theta(k)}\),
   resolving [Erdős problem 183](https://www.erdosproblems.com/183).
   Lean: [`MulticolorTriangleRamsey.lean`](https://github.com/openai/ten-proofs/blob/main/MulticolorTriangleRamsey.lean)

10. **Extremal number conjectures.** Counterexamples to the compactness
    and degeneracy conjectures in extremal graph theory, resolving
    [Erdős problem 146](https://www.erdosproblems.com/146) and
    [Erdős problem 180](https://www.erdosproblems.com/180).
    Lean: [`CompactnessAndDegeneracy.lean`](https://github.com/openai/ten-proofs/blob/main/CompactnessAndDegeneracy.lean)

Build notes from `ten-proofs`: Lean 4.32.0 + mathlib + Lake
(`lake exe cache get && lake build All`). This repo's box currently has
Lean 4.33.0 via elan; pin 4.32.0 if you want to replay their certificates
exactly.

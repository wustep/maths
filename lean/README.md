# Lean scratch

The Lake project lives at the **repository root** (same layout as
[openai/ten-proofs](https://github.com/openai/ten-proofs)):

- `lean-toolchain` — `leanprover/lean4:v4.32.0`
- `lakefile.toml` — mathlib `v4.32.0`
- `Maths.lean`, `Maths/`, `All.lean`

Use this folder for throwaway notes only. Real modules go at the root
(`Maths/<Name>.lean`) and get imported from `Maths.lean` / `All.lean`.

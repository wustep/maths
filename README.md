# maths

Private workspace for attacking hard mathematics — FrontierMath-style
problems, IMO-level contest work, and research questions in the spirit of
OpenAI's [Ten advances in mathematics](https://openai.com/index/ten-advances-in-mathematics/).

**Lean 4 is the primary environment.** Python (sympy, flint, z3, …) is a
sidecar for search, numerics, and counterexample hunting. Formal write-ups
belong in Lean, the same way [openai/ten-proofs](https://github.com/openai/ten-proofs)
ships machine-checkable certificates.

This repository is **scaffolding only**. It does not contain claimed
solutions or invented results.

## Lean (primary)

Tooling is mirrored from `openai/ten-proofs` (read via GitHub; not cloned):

| File | ten-proofs | this repo |
| --- | --- | --- |
| `lean-toolchain` | `leanprover/lean4:v4.32.0` | same pin |
| `lakefile.toml` | mathlib `v4.32.0` + Comparator | mathlib `v4.32.0` |
| layout | one `lean_lib` per result, plus `All.lean` | `Maths` lib + `All.lean` |
| build | `lake exe cache get && lake build All` | same, then `lake build Maths` |

```bash
# elan (once)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
source "$HOME/.elan/env"

cd /workspace/maths          # or your clone
elan install leanprover/lean4:v4.32.0
lake update                  # fetches mathlib @ v4.32.0
lake exe cache get           # prebuilt oleans
lake build Maths             # smoke module
lake build All
```

Add a new formalization the ten-proofs way:

1. Create `MyResult.lean` at the repo root (or `Maths/MyResult.lean`).
2. Register a `[[lean_lib]]` in `lakefile.toml` if it is a root-level target.
3. `import` it from `All.lean`.
4. Build with `lake build MyResult` (or `lake build Maths`).

ten-proofs keeps each of the ten results as a **single large root-level
`.lean` file** (`SpherePacking.lean`, `NonSoficGroup.lean`, …), an
`All.lean` that imports all of them, and a `formalization.yaml` that names
the main declarations and Comparator challenge configs. We do not copy
those proofs.

Comparator (independent kernel checking) is used by ten-proofs via
`lake exe comparator ComparatorChallenges/<file>.json`. Add that
dependency later if we have a result worth exporting; it is documented
in their [ComparatorChallenges README](https://github.com/openai/ten-proofs/tree/main/ComparatorChallenges).

## Python sidecar

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
python scripts/check_env.py
```

If `uv` is available:

```bash
uv venv .venv --python python3
uv pip install --python .venv/bin/python -r requirements.txt
```

SageMath is **not** included (too heavy).

| Area | Packages |
| --- | --- |
| CAS / numerics | `sympy`, `numpy`, `scipy`, `mpmath`, `gmpy2`, `python-flint` |
| Data / plots / graphs | `pandas`, `matplotlib`, `networkx` |
| Finite fields | `galois` |
| Optimization | `pulp`, `ortools`, `cvxpy` |
| SMT | `z3-solver` |
| Notebooks / tests | `jupyter`, `ipython`, `pytest` |

## Layout

```
lean-toolchain, lakefile.toml, Maths.lean, All.lean
Maths/            Lean library (start here)
advances/         catalog of the 10 OpenAI results (links, not copies)
problems/         attack logs for individual hard problems
notes/            working notes
src/maths/        small Python helpers
tests/            Python smoke tests
notebooks/        exploratory Jupyter
scripts/          env checker
lean/             throwaway Lean notes (project is at repo root)
```

## How we work a problem

1. Open `problems/<slug>/` (see [`problems/README.md`](problems/README.md)).
2. Write the statement and success criteria *before* computing.
3. Use Python to search / refute; formalize in Lean when an argument exists.
4. Log dead ends. Do not invent a write-up that pretends a search succeeded.

## Reproducible environment

- [`Dockerfile`](Dockerfile) — elan + Lean 4.32.0 + Python deps
- [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json)

## License

Private repository. All rights reserved unless Stephen Wu says otherwise.

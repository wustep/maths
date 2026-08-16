# maths

Notebook for a few open problems. One folder per problem. No package, no
container, no smoke tests.

## Problems

| Folder | Status |
| --- | --- |
| [covering](problems/covering) | \(\ell_2(10,2)\le 50\). Certified \([50,40]\) radius-2 code, \(p(H)=10\), propagated to \(\bar\mu(2)\le 2601/2048\). \(n=49\) still 7 holes. |
| [brocard](problems/brocard) | Lean lemmas for modular / prime-power split. Conjecture open. |
| [unique-sum](problems/unique-sum) | Rematched OEIS A398173 through \(p=47\). |
| [three-in-line](problems/three-in-line) | \(n=71\) SAT UNKNOWN. |
| [schur](problems/schur) | No 1697-coloring found. |

Each problem folder:

```
PROBLEM.md        statement and what would count as a dent
ATTACK.md         chronological attempts
WALKTHROUGH.md    discovery notes, not a cleaned proof
RESEARCH.md       papers, OEIS, failed lookups
compute/          scripts, certificates, tables
lean/             only if there is a lemma
```

## Overnight 2026-08-16

Codex proposed 50 problems; Grok+Codex picked five. Notes:

- [notes/proposed-50.md](notes/proposed-50.md)
- [notes/pick-5.md](notes/pick-5.md)
- [notes/judge-codex.md](notes/judge-codex.md)

The one finite record is the covering matrix:

`problems/covering/compute/H_r10_n50.txt`

```bash
python problems/covering/compute/verify_certificate.py
```

Written up as a standalone artifact in
[problems/covering/result](problems/covering/result) — two independent
verifiers, the \((2,0)\)-partition with \(p(H)=10\), and the QM\(_2^2\)
propagation to \(r=18,20\):

```bash
cd problems/covering/result && ./run_all.sh
```

Explainers: [HTML](problems/covering/explainer.html), [PDF](problems/covering/explainer.pdf).

## Lean

`lean-toolchain` pins Lean 4.32.0. Formal files live under the problem that
owns them, not at the repo root.

## refs

OpenAI walkthroughs, the ten-proofs PDF, and the house style live in
[refs/](refs/).

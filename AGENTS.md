# Agents

Public notebook of finite-handle attacks on open problems:
https://github.com/wustep/maths.
Stephen Wu is the human author. Models go in the README ledger.
`CLAUDE.md` is a symlink to this runbook.

## Problem folders

One folder per problem under `problems/<slug>/`.

```
PROBLEM.md              statement and what would count as a new bound
ATTACK.md               chronological attempts
WALKTHROUGH.md          discovery notes, not a cleaned proof
RESEARCH.md             papers, OEIS, failed lookups
compute/                verifier plus certificate
compute/LEAVES.md       live finite-handle queue (open / certified / residue)
compute/q<n>/           one quest
compute/q<n>/CLAIM.md   exact inequality this quest asserts (if any)
lean/                   lemmas for this problem, if any
```

Keep `ATTACK.md` chronological. Walkthrough beats:
`refs/walkthrough-style.md`. Cite URLs you opened in `RESEARCH.md`.
`lean-toolchain` pins Lean 4.32.0. Lemmas live in the problem folder.

Starting a problem: mint with `scripts/new-problem.sh <slug>`;
recipes in `.claude/skills/` (`new-problem`, `literature`,
`markdown-latex`, `compute`, `writing`);
fetch a paper with `python3 scripts/arxiv_fetch.py <id>` (optional
`--research problems/<slug>/RESEARCH.md`); OEIS via
`scripts/oeis_lookup.py`. Then add a Problems-table row. Add a
model-ledger row when you run it.

## How to work

Read `PROBLEM.md` and the published record first. arXiv is the
record; fetch and replay before trusting a number. Forum numbers
(MSE, Reddit, MathOverflow, AlphaXiv) are leads, not citations.

Before attacking, also read `compute/LEAVES.md`. If it is missing,
create it from the finite handles already in `PROBLEM.md`. Prefer
an `open` leaf. One leaf per quest. If you invent a new finite
handle, add a LEAVES row before hunting.

A new bound is a verified finite improvement of a published
record. An incomplete search is not a lower bound. Do not invent
a status noun beyond these two:

- dent — verified finite improvement of a published record. Write
  the inequality.
- residue — incomplete search (holes, SAT UNKNOWN, timeout). Not a
  lower bound.

LEAVES rows use `open` | `certified` | `residue` | `blocked`.
`certified` is a dent; `residue` is the same leftover as above.

A quest is a named campaign, not a result. Its code lives in
`compute/q<n>/`. ATTACK.md may say q3. Do not write "quest" on
README, explainers, PROBLEM, WALKTHROUGH, or other human pages.

Every quest that asserts a finite outcome keeps
`compute/q<n>/CLAIM.md`: the exact inequality or predicate, the
prior record, and what would falsify it. `run_all.sh` exit 0 means
the CLAIM holds. PROBLEM and README quote the CLAIM; do not
paraphrase a different number. A residue wrap still updates
LEAVES to `residue` and may keep the CLAIM that was attempted.

Lean is optional in `problems/<slug>/lean/` for finite algebraic
or modular claims. Do not require Lean for SAT, search, or
anneals.

README and explainers use ordinary English; ATTACK, WALKTHROUGH,
PROBLEM status lines, and skills may use dent and residue.
Independently verify every claimed number. Cite the record you
beat, or say you did not beat it.

User-facing prose follows `.claude/skills/writing`.

## What to update

Update the problem-folder files. If status changed, update the
README Problems row. When you run something, add a row to the
README “Which model ran what” table. Ledger cells name the model
(and date), never OpenAI plan/workspace labels such as 20xx or
wustep. For a dated campaign, add a
folder under `notes/` like `notes/supergrok-2026-08-17/` (REPORT +
prompts; JSONL logs stay local / gitignored).

Anything sent outside the notebook is copied to
`problems/<slug>/share/<YYYY-MM-DD>/` (the whole problem
folder at that send) and then not edited. A git tag on the send
is the pin. Later search does not go in `share/`.

`problems/` is current. `notes/lists/` catalogs, `notes/picks/`
ballots, `notes/chat/` the transcript. Those folders stay.

## Site

`web/` is a Next static export. Skip file/dir collisions
(`fileRouteCollides`). Hide `CLAUDE.md` and `vercel.json` in
`EXCLUDED_FILES` (`web/src/lib/repo.ts`). Show `AGENTS.md`.
Production: https://maths.wustep.me,
https://maths-wustep.vercel.app.
README math on github.com: `.claude/skills/markdown-latex`.

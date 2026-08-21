# Agents

Public notebook of finite-handle attacks on open problems:
https://github.com/wustep/maths.
Stephen Wu is the human author. Models go in the README ledger.
`CLAUDE.md` is a symlink to this runbook.

## Problem folders

One folder per problem under `problems/<slug>/`.

```
PROBLEM.md        statement and what would count as a dent
ATTACK.md         chronological attempts
WALKTHROUGH.md    discovery notes, not a cleaned proof
RESEARCH.md       papers, OEIS, failed lookups
compute/          verifier plus certificate
lean/             lemmas for this problem, if any
```

Keep `ATTACK.md` chronological. Walkthrough beats:
`refs/walkthrough-style.md`. Cite URLs you opened in `RESEARCH.md`.
`lean-toolchain` pins Lean 4.32.0. Lemmas live in the problem folder.

To add a problem, create that folder and those files, then add a
Problems-table row. Add a model-ledger row when you run it.

## How to work

Read `PROBLEM.md` and the published record first. arXiv is the
record; fetch and replay before trusting a number. Forum numbers
(MSE, Reddit, MathOverflow, AlphaXiv) are leads, not citations.

A dent is a verified finite improvement of a documented record.
Do not invent a dent. A failed search with a verifier is the
product. SAT UNKNOWN is not a bound. Search residue (holes,
stuck repair, timeout) is not a lower bound. Independently verify
every claimed number. Cite the record you beat, or say you did
not beat it. Claude Code recipes for these steps live in
`.claude/skills/` (literature, dent, new-problem).

## What to update

Update the problem-folder files. If status changed, update the
README Problems row. When you run something, add a row to the
README “Which model ran what” table. For a dated campaign, add a
folder under `notes/` like `notes/supergrok-2026-08-17/` (REPORT +
prompts; JSONL logs stay local / gitignored).

`problems/` is current. `notes/lists/` catalogs, `notes/picks/`
ballots, `notes/chat/` the transcript. Those folders stay.

## Site

`web/` is a Next static export. Skip file/dir collisions
(`fileRouteCollides`). Hide `CLAUDE.md` and `vercel.json` in
`EXCLUDED_FILES` (`web/src/lib/repo.ts`). Show `AGENTS.md`.
Production: https://maths.wustep.me,
https://maths-wustep.vercel.app.

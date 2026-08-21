# Agents

Public notebook of finite-handle attacks on open problems:
https://github.com/wustep/maths.
Stephen Wu is the human author. Models go in the README ledger or a
contribution statement, not a paper byline.

This file is the only agent runbook. `CLAUDE.md` is a git symlink to it.
Do not add `INSTRUCTIONS.md`. Do not keep a second copy of this text.

The README “Interesting results” table is the status line. Do not
duplicate it here.

## How a problem is organized

One folder per problem under `problems/<slug>/`.

```
PROBLEM.md        statement and what would count as a dent
ATTACK.md         chronological attempts
WALKTHROUGH.md    discovery notes, not a cleaned proof
RESEARCH.md       papers, OEIS, failed lookups
compute/          scripts, certificates, tables
lean/             only if there is a lemma
```

Keep `ATTACK.md` chronological as you go.
Walkthrough beats: `refs/walkthrough-style.md`. Empty sections mean
the quest is not done.
Write `RESEARCH.md` with URLs actually opened.

`compute/` is one verifier plus the certificate.

`lean-toolchain` pins Lean 4.32.0. Formal files live under the
problem that owns them, not at the repo root.

To add a problem, create that folder and those files, then add a
Problems-table row. Add a model-ledger row when you run it.

## How to work a problem

Read `PROBLEM.md` and the published record first. arXiv abs/HTML/PDF
is the record; fetch and replay before trusting a number. Forum
numbers (MSE, Reddit, MathOverflow comments, AlphaXiv) are leads,
not citations.

A dent is a verified finite improvement of a documented record.
Do not invent a dent. A failed search with a verifier is the product.
SAT UNKNOWN is not a bound. Search residue — holes, stuck repair,
timeout — is not a lower bound.

Independently verify every claimed number. Cite the record you beat,
or say you did not beat it.

Keep attack logs in the problem folder and git. Do not invent
numbers, timings, or menus.

## What to update when you finish a run

Always update the problem-folder files above.

Root README: the status row in the Problems table if the status
changed; a row in “Which model ran what” when you ran something.
Do not revive `notes/process/` or a log/learnings file.

If it is a dated multi-problem campaign, a folder under `notes/`
like `notes/supergrok-2026-08-17/` (REPORT + prompts; JSONL logs
stay local / gitignored) is the template. Do not restructure
`notes/lists/`, `notes/picks/`, or `notes/chat/` unless asked.

## Notes vs problems

`problems/` is current. The README table is the status line.

- `notes/lists/` — catalogs
- `notes/picks/` — dated ballots
- `notes/chat/` — transcript recreation

## Site

`web/` is a Next static export. `output: "export"` and
`trailingSlash` are load-bearing. Colliding file/dir routes stay
skipped (`fileRouteCollides` in `web/src/lib/repo.ts`).

The file-viewer hide list is `EXCLUDED_FILES` in
`web/src/lib/repo.ts`. Keep `web/scripts/collect-raw.mjs` in sync.
Hide `CLAUDE.md` and `vercel.json`. Show `AGENTS.md`.

Production: https://maths.wustep.me and
https://maths-wustep.vercel.app.

## Style

`refs/walkthrough-style.md`. One verb for a check: verify.
No agent-story.

## House

- Do not purchase extra SuperGrok usage or enable auto top-up.
- Effort flag is `xhigh`. `max` is invalid.
- Do not email outside authors or send unpublished search code or
  unreleased matrices from this workspace. Point at the public
  repo. Do not add third-party PDFs you were sent.

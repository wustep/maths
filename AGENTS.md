# Agents

Notebook of finite-handle attacks on open problems.
Public repo: https://github.com/wustep/maths.
Stephen Wu is the human author. One interesting result so far.

This file is the only agent runbook. `CLAUDE.md` is a git symlink to it.
Do not add `INSTRUCTIONS.md`. Do not keep a second copy of this text.

## Covering

A binary linear code of length 50 and dimension 40 has covering radius
exactly 2. The $10\times 50$ parity-check matrix
`problems/covering/compute/H_r10_n50.txt` hits every syndrome in
$\mathbb{F}_2^{10}$ as a sum of at most two columns (1024/1024,
two independent verifiers). That is

$$
\ell_2(10,2)\le 50.
$$

Construction, upper bound, not a conjecture. The November 2025 table
(Davydov–Marcugini–Pambianco, arXiv:2511.02542, Table 5.1) had
$\ell_2(10,2)\le 51$. Sphere covering still only gives $\ge 45$.
An $n=49$ search left 7 holes, so 50 is not shown optimal.
$r=11$ is still the paper 79.

The same matrix has a $(2,0)$-partition with $p(H)=10$. The
$\mathrm{QM}_2^2$ construction then produces longer codes
($r=18$, $n=815$; $r=20$, $n=1631$) and the density bound
$\bar\mu(2)\le 2601/2048\approx 1.27002$. That is the interesting
part: a finite seed that moves the asymptotic constant, not just a
table entry.

Do not claim $n=49$, $f(2)=1$, or a gapless even-$r$ family.

Replay:

```bash
python problems/covering/compute/verify_certificate.py
cd problems/covering/result && ./run_all.sh
```

Later QM and partition lifts, and their scripts, are on the root
README. Standalone writeup: `problems/covering/result`.

## Folder contract

Each problem folder:

```
PROBLEM.md        statement and what would count as a dent
ATTACK.md         chronological attempts
WALKTHROUGH.md    discovery notes, not a cleaned proof
RESEARCH.md       papers, OEIS, failed lookups
compute/          scripts, certificates, tables
lean/             only if there is a lemma
```

Walkthrough beats: `refs/walkthrough-style.md`. Empty sections mean
the quest is not done. Keep `ATTACK.md` chronological as you go.
Write `RESEARCH.md` with URLs actually opened.

`lean-toolchain` pins Lean 4.32.0. Formal files live under the
problem that owns them, not at the repo root.

## Dent vs residue

A dent is a verified finite improvement of a documented record: a
shorter covering length, a better constant, a construction that
moves a table, a lemma.

Do not invent a dent. A failed search with a verifier is the product.
SAT UNKNOWN is not a bound. Search residue — 7 holes at $n=49$, a
stuck repair, a timeout — is not a lower bound.

Forum numbers (MSE, Reddit, MathOverflow comments, AlphaXiv) are
leads, not citations. arXiv abs/HTML/PDF is the record; fetch and
replay before trusting a number.

Independently verify every claimed number. Cite the published record
you beat, or say you did not beat it.

## compute/

One verifier plus the certificate. Keep attack logs in the problem
folder and git.

## Notes vs problems

`problems/` is current. The README table is the status line.

- `notes/lists/` — catalogs (the 50, Hilbert, Smale, Landau).
- `notes/picks/` — dated ballots.
- `notes/supergrok-2026-08-17/` — dated SuperGrok run: `REPORT.md`
  and prompts. JSONL logs stay local / gitignored.
- `notes/chat/` — Grok Bot transcript recreation (on main).

Do not restructure those folders unless asked. Do not write a
replacement log or learnings file.

## Site

`web/` is a Next static export of the repo markdown.
`output: "export"` and `trailingSlash: true` are load-bearing.
A file route that collides with a directory (notably
`notes/chat/index.html` next to `notes/chat/`) must stay skipped
(`fileRouteCollides` in `web/src/lib/repo.ts`).

Production: https://maths.wustep.me and
https://maths-wustep.vercel.app.

The file-viewer hide list is `EXCLUDED_FILES` in
`web/src/lib/repo.ts`. Keep `web/scripts/collect-raw.mjs` in sync.
Hide `CLAUDE.md` and `vercel.json`. Keep showing `AGENTS.md`.

## Attribution

Stephen Wu is the human author. Models belong in the README ledger
or a contribution statement, not a paper byline. When you run
something, add a row to the README table. Do not revive
`notes/process/models.md`.

## Style

User-facing math notes follow `refs/walkthrough-style.md`.
GitHub markdown math uses `$` / `$$`.
One verb for a check: verify. No agent-story. No invented numbers,
timings, or menus.

## House

- Do not purchase extra SuperGrok usage or enable auto top-up.
- SuperGrok effort flag is `xhigh`. `max` is invalid.
- Do not email Davydov–Marcugini–Pambianco. Do not send unpublished
  search code or unreleased matrices from this workspace. Point at
  the public repo. IITP RAS is sanctioned; keep correspondence
  personal if Stephen asks later. Do not add their PDF
  (`problems/covering/compute/notes_from_authors_2026-08-19.md`).
- The priority checklist in `problems/covering/result/PRIORITY.md`
  is for a human. Nothing goes out before that.

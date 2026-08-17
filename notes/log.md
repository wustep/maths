# Log

Repo history and general runs. Problem-local notes stay in each folder
(`ATTACK.md`, `WALKTHROUGH.md`, `RESEARCH.md`). Model table:
[process/models.md](process/models.md).

Public repo: https://github.com/wustep/maths

## 2026-08-16

- Started as a Lean-first workspace, then flattened to five problem folders
  plus `notes/` and `refs/`. Pushed public as `wustep/maths`.
- Codex proposed 50 problems (`notes/lists/2026-08-16-proposed-50.md`). Grok+Codex
  picked five overnight under a 50% Codex cap. Hofstadter (P13) skipped
  (already settled, arXiv:2608.07910).
- Overnight solvers: Codex `gpt-5.6-sol` Max on covering, Brocard,
  unique-sum, three-in-line (n=71), Schur S(7). The one finite record is
  the covering matrix: \(\ell_2(10,2)\le 50\), binary \([50,40]_2\)
  radius-2, \(p(H)=10\). Not shown optimal.
- Afternoon: Cursor Grok 4.6 on van der Waerden \(W(2,7)\) (P42) and
  Shannon \(C_7\) fifth power (P21). Both failed to beat the known
  constructions (3703 residue coloring; Polak–Schrijver 367-set). Few-flip
  SAT: no 368-set within Hamming distance 9 of 367.
- Covering packaged as PR #3 (`0f79fcc`): `result/` with QM₂²
  propagation, alternate \(r=18/20\) matrices, no `_reference/` scaffold.
  Explainers: HTML (Claude Opus 5 and Fable 5) and a LaTeX/PDF with
  verified numbers. Byline: Grok Bot (4.6), Claude Opus 5, Claude Fable 5,
  GPT Sol 5.6, plus a small Stephen Wu instruction line. How to re-run
  is repo-standalone (`git clone` of this repo).
- PRs #1 (C7) and #2 (W(2,7)) merged to main. Draft PR #4
  (`draft/grokbot-chat-transcript`) is a 1:1 HTML+JSON of the Grok Bot
  thread; not merged.

## 2026-08-17

- Added Hilbert 23, Smale 18, and Landau 4 lists
  (`notes/lists/{hilbert,smale,landau}.md`). Dated the 50-list and the pick files; dropped the one-line path stubs.
  Ideation pick: Landau 4
  (infinitude of primes \(n^2+1\)).
- Started `problems/landau-n2-plus-1`. Certified prefix: exactly 12391
  primes \(n^2+1\) for \(n\le 200000\) (includes \(2=1^2+1\)). First
  values match OEIS A002496. Not infinitude.
- Notes sorted into `lists/`, `picks/`, `process/`.
- README: dropped the Overnight 2026-08-16 section; Interesting results now leads with covering.
- SuperGrok CLI (`grok-4.6`, effort `xhigh`) started on three new
  problems from the 50, using the weekly SuperGrok pool (no Extra Usage
  purchase):
  - P29 unit-distance 509 → `problems/unit-distance-509`
  - P07 Sidon second term → `problems/sidon-second-term`
  - P15 Chowla cosine → `problems/chowla-cosine`
  - plus Landau 4 as a fourth run
  Prompts live in `notes/supergrok-2026-08-17/`. JSONL logs stay local
  (gitignored). House rule: each run writes only under its own folder;
  no invented dents; no git from the CLI.

- SuperGrok P07 (Sidon) and P15 (Chowla) finished. Verified: Hou–Zhao L=6 lift (8e-8 below γ0, does not change 0.9435); Chowla K(n) ≥ n^{1/7}/18 (does not beat Bedert 1/5−o(1)). Report: notes/supergrok-2026-08-17/REPORT.md. Next launches: P14 two-squares, P16 cosine zeros. Keep going until ~10% weekly SuperGrok remains.

## Open / in flight

- SuperGrok four-run watch (P29, P07, P15, Landau 4). Wrap before the
  weekly pool dies. Do not buy more usage.
- Draft PR #4 chat transcript: leave unmerged unless asked.
- Covering authors (arXiv:2511.02542) not yet emailed. Construction, not
  a conjecture; 50 is an upper bound, not shown optimal.

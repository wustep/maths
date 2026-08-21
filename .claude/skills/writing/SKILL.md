---
name: writing
description: Draft or edit user-facing markdown in this repo. Use when writing or revising README, PROBLEM.md status, explainers, notes, or GitHub pull request titles and bodies.
---

# Writing

Tao: say what you prove, define notation, skip "it is easy to see"
and throat-clearing, one claim per sentence.

README, PROBLEM.md status, explainers, notes, and GitHub PR titles
and bodies. ATTACK.md stays chronological. Walkthroughs stay
`refs/walkthrough-style.md`. The dent skill decides the status.
Write that status once.

## Math

Construction, upper bound, replay, or residue. Define a symbol
the first time it appears. Cite the record once.
Residue is a failed search with a verifier.
Do not narrate the ten things it is not.

## Sentences

One idea per sentence. Active voice. Name the actor. Prefer the
verb: verify, not "perform a verification." Cut "note that",
"it is worth mentioning", "serves as", "not just X but Y".

## Slop

Cut puffery and AI vocabulary (delve, showcase, pivotal,
landscape, robust, comprehensive). No em dashes. Pick one verb
for the same act. No forced lists of three.

## Hedges

Keep a hedge only when the claim is actually open. Delete hedges
that only deny a misreading. "Not shown optimal" sits next to
the open gap, not after every length. Caveat once, in a status
line.

## Before / after

README covering, same numbers.

Before: The November 2025 table (Davydov–Marcugini–Pambianco,
arXiv:2511.02542, Table 5.1) had $\ell_2(10,2)\le 51$. This is a
construction, an upper bound, not a conjecture. Sphere covering
still only gives $\ge 45$, and an $n=49$ search left 7 holes, so
50 is not shown optimal.

After: The November 2025 table (Davydov–Marcugini–Pambianco,
arXiv:2511.02542, Table 5.1) had $\ell_2(10,2)\le 51$. Status:
construction; sphere covering $\ge 45$; $n=49$ still 7 holes.

## Pull requests

The title is the change. The body says what changed and how to
replay or check. No "this PR aims to." No chatbot close.

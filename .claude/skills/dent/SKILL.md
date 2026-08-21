---
name: dent
description: Decide whether a result is a dent or residue, and write the claim honestly. Use before claiming any bound, improvement, or record, and when writing up a search that found nothing.
---

# Dent

A dent is a verified finite improvement of a documented record.
All three words carry weight.

- **Verified**: independently check every claimed number — a
  second implementation or a replay path (`run_all.sh`) a
  stranger can execute. Verifier plus certificate go in
  `compute/`.
- **Documented record**: cite the specific thing you beat (paper,
  table, entry — e.g. "arXiv:2511.02542 Table 5.1 had ≤ 51").
  If you did not beat it, say so plainly: "No dent." is a valid
  README status and many rows carry it.

Not bounds, ever:

- SAT UNKNOWN is not a bound.
- Search residue — holes, stuck repair, timeout — is not a lower
  bound.
- An SDP float with no exact certificate is not a dent.
- A table of minima for a few instances is residue.

Residue is still worth recording: put it in `ATTACK.md` and the
README status ("n=49 still 7 holes"), just never promote it to a
claim. A failed search with a verifier is the product — write it
up as exactly that.

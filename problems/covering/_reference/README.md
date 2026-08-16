# Reference kit — covering code result (r=10, n=50)

Generated alongside the Claude Code prompt. **This is scaffolding, not the
deliverable.** Everything here is meant to be superseded by what Claude Code
writes into `problems/covering/result/`.

## QUARANTINE PROTOCOL — read this first

`scripts/oracle_check.py` is a working verifier. If Claude Code reads it before
writing `verify/`, you get one implementation wearing two hats, and the whole
point of independent verification is lost.

So:

1. Drop this kit at `problems/covering/_reference/` and tell Claude Code:
   **"Do not read `_reference/scripts/` until both verifiers in `verify/` are
   written and passing. Then diff your results against the oracle."**
2. `data/` is safe to read at any time — those are inputs and generated
   matrices, not verification logic.
3. After Claude Code's verifiers pass, run the oracle and confirm agreement.
   Two independent implementations agreeing on 262144 and 1048576 exhaustive
   syndrome enumerations is the actual evidence.
4. Delete `_reference/` before committing the result, or keep it and say
   plainly in the note that it was the scaffold.

## Contents

```
data/
  H_r10_n50.txt        the [50,40]_2 code, covering radius 2   <- the result
  partition_p10.json   (2,0)-partition into 10 blocks          <- the new ingredient
  kr_r10_n51.txt       Kaikkonen-Rosendahl 2003 baseline, reconstructed from hex
  H_r18_n815.txt       QM_2^2 at m=4   (published best: 831)
  H_r20_n1631.txt      QM_2^2 at m=5   (published best: 1663)
scripts/
  gen_data.py          deterministic, no RNG; regenerates all of data/
  oracle_check.py      QUARANTINED reference verifier
```

## Verified facts (all reproduced by `oracle_check.py` from matrix text alone)

| | value |
|---|---|
| r=10 | n=50, 1024/1024, rank 10, density 319/256 = 1.24609375 |
| baseline | KR 2003: n=51, density 1327/1024 = 1.29590 |
| partition | p(H) = 10, vs the paper's computer-searched p(H_KR) = 11 |
| minimality | deleting ANY column leaves >= 9 syndromes uncovered -> LO code |
| distance | d = 3; 10 dependent triples; one spans 3 distinct blocks |
| r=18 | n=815, 262144/262144, density 332521/262144 = 1.268473 |
| r=20 | n=1631, 1048576/1048576, density 1330897/1048576 = 1.269247 |
| family | n = 51*2^(r/2-5) - 1, density -> 2601/2048 = 1.269995 |

## Two things worth putting in the note that aren't in the prompt

**Minimality.** The 50-set is a *minimal* 1-saturating set in PG(9,2),
equivalently a locally optimal (LO) covering code in the sense of
Davydov-Giulietti-Marcugini-Pambianco. Deleting any single column leaves at
least 9 syndromes uncovered. This forecloses the obvious referee question
("is it padded?") and connects to an existing literature.

**The dependent triple.** Columns 491, 734, 821 sum to zero and lie in blocks
6, 4, 9 — three distinct blocks. This is the exact analogue of the paper's
Theorem 5.2(ii) (h5 + h27 + h29 = 0 across distinct subsets), which they needed
to run the QM_5^2 step at r=28. The new seed inherits the property, so the
r=28 branch of the iteration should carry over too. Worth verifying explicitly
rather than assuming.

## Known soft spot

m=4 and m=5 from the base seed are exhaustively verified. Steps beyond that
(iterating from the 815-column code at r=18) rest on the paper's stated bound
p(H_C) <= 2^(m+1)+1 rather than on directly computed partitions. If budget
allows, compute those partitions explicitly instead of inheriting the bound.
That is the weakest link in the family claim.

## Constants

GF(16): x^4 + x + 1 (0x13).  GF(32): x^5 + x^2 + 1 (0x25).
Column encoding: bit i (LSB first) = row i+1.
KR hex in arXiv:2511.02542 Thm 4.3 is MSB-first with row 1 as MSB;
`gen_data.py` reverses it to the LSB-first convention used everywhere else.
Getting this backwards is the most likely source of a spurious mismatch.

---

## Note added 2026-08-16 afternoon (by the session that consumed this kit)

`scripts/` and `covering-reference-kit.tar.gz` have been **deleted** from this
branch. The quarantine held: `scripts/oracle_check.py` was not read until both
verifiers in `../result/verify/` were written and `../result/run_all.sh` was
green, and it was then run exactly once as a post-hoc third opinion. It agreed
on every value. No oracle code was copied, so keeping it in the tree would only
blur which implementation is which.

`data/` is kept. Its `H_r18_n815.txt` and `H_r20_n1631.txt` are *different*
matrices from the ones in `../result/data/` — the indicator allocation in
Construction QM is a free choice — and both sets pass the full exhaustive
check, so they stand as independent second witnesses at r = 18 and r = 20.
`CLAUDE_PROMPT.md` is kept as the brief this work was done against.

The deliverable is `../result/`.

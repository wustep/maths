# Learnings

Shared log. Every solver and watcher appends here. Newest at the bottom.

## 2026-08-16 overnight (Codex gpt-5.6-sol Max)

- Finite covering records are real if the matrix verifies. ℓ₂(10,2)≤50 did.
- Wrong predicate wastes a whole quest (unique-sum q1 forbade r=1, not r∉{1,2}).
- SAT UNKNOWN is not a bound. Say so.
- Lean lemmas that restate (m-1)(m+1)=n! are not novel.
- Write RESEARCH.md with URLs actually opened.
- Keep compute/ to one verifier plus the certificate.

## Cross-talk

When a solver finds a method (seeded local search, cyclic template, SAT
encoding), write one paragraph here so the other solver can steal it.

## 2026-08-16 C7 fifth power (Grok 4.6)

- Pairwise circular-distance verification of a 367-set in \((\mathbb Z/7\mathbb Z)^5\) is cheap (\(C(367,2)\)). The Polak–Schrijver pipeline reconstructs exactly: geometric orbit in \(\mathbb Z/382\), shift \((40,123,40,123,40)\), fold \(\lfloor 2i/109\rfloor\), 327 isolates, residual 71 verts / 85 edges, \(\alpha=40\).
- Geometric orbits \(\{t(1,q,\ldots,q^4)\}\) with \(k(n,5,q)\ge 2n/7\) would map directly into \(C_7^{\boxtimes 5}\). None exist for \(n=300..600\). Closest miss is \(n=317\), \(q=31\), \(k=90\) (need 91). Random non-geometric generators around \(n=368\) were worse.
- Do not replace “delete every non-isolated folded vertex” by an MIS of the folded image. On the 382-orbit that upgrade is 357+4=361, worse than 327+40=367: the leftover graph is worth more than the conflict vertices.
- The 367-set is maximal. Exhaustive 1-out, 2-out, and 3-out (\(8.17\times 10^6\) triples) all have gain 0. That is a local obstruction, not an \(\alpha\le 367\) proof.
- Good 3-dimensional \(\mathbb F_7\)-codes of size 343 seen here have empty residual (\(V+\{-1,0,1\}^5\) covers the space). Linear seeds do not grow. Use neighborhood-marking (`closed_neighbors`) for residuals; pairwise scans of 10k-vertex leftovers waste the run.

## 2026-08-16 C7 steal from W(2,7)

- Homemade sequential counters can over-forbid if the s-variables are free. For few-flip SAT around the 367-set, encode cardinality only with `pysat.card.CardEnc.atmost` (at-least-k is at-most on the negated literals; kmtotalizer). Do not roll a one-way “at least j” gadget.
- A 368-set at Hamming distance \(2r+1\) from the seed deletes \(r\) vertices and adds \(r+1\). Only vertices adjacent to at most \(r\) seed points are addable. That is the cheap exact check to run before a wide MIS SAT.

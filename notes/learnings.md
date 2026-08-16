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

## 2026-08-16 vdw-w27 (Grok 4.6)

The published \(W(2,7)>3703\) coloring is the Paley 2-coloring of \(\mathbb Z/617\mathbb Z\) unfolded six times plus one extra bit. It does not extend: color \(0\) at \(3704\) completes the class-\(2\) progression of difference \(617\), color \(1\) completes six other 7-APs, and flipping any class-\(2\) point creates a difference-\(11\) (or \(285\)) 7-AP. Cadical with a real at-most-\(k\) encoding refuted \(\le 6\) flips of that seed and also refuted rewriting the last period (\(619\) free bits) of the five-period prefix. A homemade sequential counter that only implied “at least \(j\) flips” one way was unsound — the \(s\) variables could be set true freely and over-forbid flips; use `pysat.card.CardEnc.atmost`. Herwig’s zip without the turn is just the \(617\) cycle repeated; the turned zip has complementary halves (the exact condition that makes difference-\(617\) 7-APs alternate) but CEGAR stayed at \(\sim 11000\) cyclic 7-APs. No QR prime in \(619..50000\) has monochromatic run \(\le 6\). Seeded min-conflicts from the \(3703\) coloring repeatedly stalls at one leftover 7-AP — treat that as a local cage, not as evidence that \(3704\) is impossible.

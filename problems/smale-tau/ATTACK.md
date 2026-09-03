# Attack log — smale-tau

Chronological attempts, newest last. A failed attack belongs here too.

## 2026-09-02 — mint, literature, choice of the finite handle

- Read Smale 1998 (Problem 4), Shub–Smale 1995, Bürgisser 2006/2009,
  Koiran 2004, Markström 2014, OEIS A173419 and A217032, and the 2013
  contest pages (RESEARCH.md).
- The polynomial statement has no finite record to move: no table of the
  largest \(Z(f)\) for \(\tau(f)\le k\) exists in the literature, so a
  table would be new data, not a dent. Smale's own text puts the integer
  question \(\tau(k!)\le(\log k)^c\) inside Problem 4, and there the
  record is finite and explicit: \(\tau(n!)\) is known for \(n\le 19\),
  and \(20!,21!,22!\) sit at \(13\le\tau\le 14\).
- q1: complete 13-step search with exact arithmetic, deciding
  \(\tau(20!),\tau(21!),\tau(22!)\), plus \(29\#\) and \(31\#\) where
  Markström's bounds leave a gap of three. Details in
  `compute/q1/README.md`.

## 2026-09-02 — q1 controls

- Count mode replays Markström's Figure 1 exactly for \(k\le 9\)
  (2, 4, 9, 26, 102, 562, 4363, 46154, 652227) and OEIS A173419 for
  \(n\le 1800\) with no mismatch; the four Patanè primes below 5000
  (3359, 3623, 4909, 4943) come out with the stated values.
- The three-step endgame agrees with a brute-force Python expansion on
  7485 random (prefix, target) pairs at prefix depths 3–6, and with an
  independent Rust brute-force expansion (`compute/q1/check.rs`) on
  11991 pairs at prefix depths 7, 9 and 10, of which 11991 include 7991
  genuinely reachable targets. The Rust enumerator, written separately
  with different data structures, reproduces the node counts per depth
  through depth 9 (1, 2, 8, 59, 663, 10609, 225219, 6057298, 199290037)
  and the same reached-set sizes.
- Decisions at 11 and 12 steps replay the 2013 record: 13! and 14! in 11
  steps, none of 15!–22! in 11; the 12-step run is the second control
  (see below).
- Speed work: the first endgame did about a thousand hash lookups per
  target per leaf. A size bound (a target that is neither a square nor a
  cube needs \(\max S^5\ge N\) to be reachable in three steps), range
  checks before every lookup, divisor sets instead of 128-bit divisions,
  and a bit-length scan instead of a limb division cut the 11-step run
  from 187 s to 50 s on 8 threads.

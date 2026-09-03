# Proposed OEIS updates from q1

Drafts for Stephen to submit; nothing here has been sent.

## A173419 (τ(n), programs from 1 with +, −, ×)

- b-file extension: `tau_table_10266.txt` gives τ(n) for 1 ≤ n ≤ 10266,
  agreeing with the existing b-file for n ≤ 1800. Every n ≤ 10266 is
  reached within 9 steps (10267 is the least n with τ(n) = 10, A141414),
  so the table is exact. Computed twice (C and Rust) by exhaustive
  enumeration of all normalised programs of at most 9 steps.
- Comment check: the four primes p < 5000 with τ(p) < τ(p−1) are 3359,
  3623, 4909, 4943, as stated in the comment of 28 Aug 2026.

## A217032 (τ(n!))

- a(13)–a(19) replayed: complete 11-step and 12-step searches with exact
  arithmetic (no modular reduction, no size cap) confirm 13! and 14! at 11,
  15!, 16!, 17! at 12, and no 12-step program for 18! and 19!.
- a(20), a(21), a(22): pending the 13-step decision (this folder,
  `decide13.json`).

## Primorials (no OEIS entry found for τ(p#))

- τ(29#) = 12 and τ(31#) = 12, with programs in `decide12.json`; the
  lower bound 12 is the complete 11-step search. Markström (INTEGERS 14,
  2014, Figure 5) had 13 and 15.

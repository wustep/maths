# Smale 4 τ-conjecture, mint and q1, 2026-09-02/03

Result: exhaustive straight-line-program searches with exact arithmetic give

    τ(29#) = 12  (Markström 2014 had ≤ 13),
    τ(31#) = 12  (Markström 2014 had ≤ 15),

and [FILL: the 13-step decision for 20!, 21!, 22!].

The polynomial statement of Problem 4 has no finite record to move, so the
campaign took the integer question that Smale states in the same problem,
whether τ(k!) ≤ (log k)^c. The record there was OEIS A217032 and
Markström's tables: τ(n!) exact for n ≤ 19, and 13 ≤ τ(n!) ≤ 14 for
n = 20, 21, 22.

Controls before any claim: the enumerator reproduces Markström's counts of
integers reachable within k ≤ 9 steps (2, 4, …, 652227), the OEIS A173419
b-file for n ≤ 1800 (extended here to n ≤ 10266 by two implementations),
and the 11- and 12-step contest record (13!, 14! at 11; 15!, 16!, 17! at
12; nothing at 12 for 18!–22!). A Rust re-implementation matches node counts
through depth 9, and brute-force expansions of the three-step endgame agree
on about forty thousand random (prefix, target) pairs.

Polynomial side (q2): exact enumeration over Z[x] with rigorous root-count
filters gives the largest number of distinct integer zeros at cost k ≤ 6 as
1, 1, 2, 3, 3, 4, 5; six steps already give five zeros via x((x²−2)²−x²).
[FILL: k = 7.]

Replay:

```sh
cd problems/smale-tau/compute/q1 && ./run_all.sh        # controls, 11- and 12-step decisions
cd problems/smale-tau/compute/q1 && ./run_all.sh --full # adds the 13-step decision (hours)
cd problems/smale-tau/compute/q2 && ./run_all.sh        # polynomial table through k = 6
```

Certificates: `problems/smale-tau/compute/q1/certificate.json` and
`problems/smale-tau/compute/q2/table.json`.

Claude Fable 5.1 ran the searches. Stephen Wu is the human author of the
notebook.

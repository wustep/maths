# Walkthrough — smale-tau

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.
Empty beats mean the quest is not done.

0. What was actually missing — a finite handle. The polynomial
   conjecture \(Z(f)\le a\tau(f)^c\) has no published table to move, and
   any table of small cases would be new data rather than an improvement.
   The degree of freedom was to read Smale's own text of Problem 4 to the
   end: it carries the integer question \(\tau(k!)\le(\log k)^c\), whose
   finite record is explicit (OEIS A217032, Markström 2014) and stops at
   \(19!\). The next three terms sit in a gap of one step.

1. Named false starts —
   - Reading the conjecture as being only about polynomials and planning a
     table of \(\max Z(f)\) over \(\tau(f)\le k\). Small hand cases
     (\(x^3-x\) at 3 steps, \((x^2-2x)(x^2-1)\) at 5 steps) showed the
     table would start at 1, 1, 2, 3, 3, 4 and beat no record.
   - Storing a hash set of every divisor of every factorial up to 34!:
     12 million divisors for 34! alone pushed memory past 3 GB. Replaced
     by trial division by the target's own primes for large targets.
   - A first endgame with about a thousand hash lookups per target per
     leaf: the 11-step replay took three minutes, extrapolating to days at
     13 steps. Range and size filters cut it by four.

2. The useful failure — the size filter needed a proof: three steps
   raise the maximum \(M\) of the set to at most \(M^8\), but only through
   \(N=y_2^2\) or \(N=y_1^3\); a target that is neither a square nor a
   cube needs \(M^5\ge N\). Factorials and primorials are never perfect
   powers, so more than half of all (leaf, target) pairs vanish before
   any lookup.

3. The click — Rokicki's pending queue from the 2013 contest list gives a
   canonical order that visits every normalised program exactly once, and
   a three-step endgame turns a depth-13 tree into a depth-10 tree with a
   constant-size case analysis at each leaf.

4. The argument — in `compute/q1/README.md`: normalisation (positive,
   distinct), the lexicographically least valid order, and the complete
   case split of the last three steps.

5. Computer search — `compute/q1`: counts through 9 steps match
   Markström's Figure 1, \(\tau(n)\) for \(n\le 1800\) matches OEIS
   A173419, the endgame matches a brute-force expansion on 7489 random
   pairs, and the 11-step and 12-step decisions replay the contest record.
   (13-step run: pending.)

6. Proven vs still open — pending the 13-step run.

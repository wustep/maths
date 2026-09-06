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
   constant-size case analysis at each leaf. The second click was that the
   same machinery decides *any* small target for free: the primorials
   \(29\#\) and \(31\#\), where Markström's bounds had gaps of one and
   three steps, came out at exactly 12 in the 12-step run, three steps
   under the printed 15 for \(31\#\).

4. The argument — in `compute/q1/README.md`: normalisation (positive,
   distinct), the lexicographically least valid order, and the complete
   case split of the last three steps. The primorial programs are short
   enough to check by hand: \(31\#=10010\cdot 2001\cdot 10013\) with
   \(10010=1001\cdot 10\), \(2001=1000+1001\), \(10013=10010+3\); and
   \(29\#=14630\cdot(665^2-4)\) with \(665=19\cdot 35\), \(14630=665\cdot 22\).

5. Computer search — `compute/q1`: counts through 9 steps match
   Markström's Figure 1, \(\tau(n)\) for \(n\le 1800\) matches OEIS
   A173419 and the table is extended to \(n\le 10266\) by two
   implementations, the endgame matches brute-force expansions (Python and
   Rust) on about forty thousand random pairs, and the 11-step and 12-step
   decisions replay the contest record. `compute/q2`: the polynomial
   table \(T(k)=1,1,2,3,3,4,5\) for \(k\le 6\), with the surprise that
   six steps already give five integer zeros through
   \(x\bigl((x^2-2)^2-x^2\bigr)\). (13-step run: residue — incomplete.)

6. Proven vs still open — proven: \(\tau(29\#)=\tau(31\#)=12\), the
   replayed values \(\tau(n!)\) for \(13\le n\le 19\), \(T(k)\) for
   \(k\le 6\). Residue: the 13-step decision for \(20!\), \(21!\),
   \(22!\) (and \(37\#\)) did not finish. Open: everything Smale asked;
   nothing here touches the conjecture or the growth of \(\tau(k!)\).

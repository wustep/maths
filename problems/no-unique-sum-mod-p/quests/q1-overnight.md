# Quest q1 — exact m(p) for primes p≤200

- Model: gpt-5.6-sol Max
- Started: (parent fills)
- Status: ready
- Cost: S
- Shape: finite-cex

## Idea

\(m(p)\) is a finite search. Exhaust small primes; SAT / Z3 / cardinality
SAT for the rest up to 200. Match OEIS A398173 on \(p\le 47\), then
extend. Plot against \(\log p\) and \((\log p)^2\). Write down what the
extremal sets look like (interval, balanced, symmetric square, other).

## Solve prompt

```
Read PROBLEM.md and this quest file. Attempt only this quest.

Compute the exact integer m(p) for every prime 3 ≤ p ≤ 200.
A set A ⊆ Z/pZ, |A|≥2, has no unique sum iff every s in A+A has at
least two unordered representations as {a,b} from A (repetition
allowed); equivalently, for odd p, the ordered representation
function satisfies r_A(s) ∉ {1,2} for all s.

Do this:
1. Exhaustive search for small p (at least through the OEIS A398173
   range p≤47). Confirm the 14 published terms
   3,4,5,7,7,8,9,10,11,11,12,13,13,13.
2. SAT / Z3 / pysat cardinality search for the remaining primes
   p≤200. Write the encoding in compute/. Prefer a minimisation
   that proves no smaller set exists, not just a feasible witness.
3. Dump compute/m_p.csv with columns p,m,witness. Independently
   re-run the no-unique-sum check on every witness.
4. Plot m(p) against log p and against (log p)^2 using
   /maths/src/maths/figures.py. Save under figures/ and embed.
5. Write the shape of the extremal sets (interval / Nedev-balanced /
   Cao–Yuan C+C / other). One paragraph plus examples.
6. Optional Lean: NoUniqueSum predicate and one small certified
   witness (m(5)=4 is enough).

Do not attack the log p log log p vs (log p)^2 asymptotic.

Write Lean under lean/, Python under compute/.
If the residue is a region, bound, graph, or counterexample, save a PNG
under figures/ (use /maths/src/maths/figures.py) and embed it from
ATTACK.md, this quest file, and WALKTHROUGH.md.

Append what you did to ATTACK.md. Do not claim a solve unless Lean
builds or the counterexample is explicit and independently re-run.
Do not start a second quest. If blocked, write the residue and stop.

Write WALKTHROUGH.md in the OpenAI "How the Ideas Came Together" style:
false starts, the useful failure, the click, the argument, what is
proven vs still open. Follow /maths/loop/walkthrough-style.md. If that
file is missing, read /maths/loop/refs/reasoning-walkthroughs.txt.

```

## What happened

## Residue (what the next quest should know)

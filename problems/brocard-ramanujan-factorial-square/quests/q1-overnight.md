# Quest q1 — modular obstructions and one Lean lemma

- Model: gpt-5.6-sol Max
- Started: (parent fills)
- Status: ready
- Cost: S
- Shape: short-lean

## Idea

The conjecture is out of reach. The overnight handle is local:
quadratic-residue sieves, covering systems, and one sharp modular
lemma in Lean. Re-run Berndt–Galway's method on a slice you can
finish. Do not claim there are no other Brown numbers.

## Solve prompt

```
Read PROBLEM.md and this quest file. Attempt only this quest.

Mine modular / covering-system obstructions to n!+1=m^2 beyond
the textbook ones; re-run a published computational range; Lean-
formalize ONE sharp modular lemma. Do not claim the conjecture.

Do this:
1. Write the informal skeleton of the Lean lemma first. Suggested
   target (change only if you find a sharper true lemma):
     If n!+1=m^2, p prime, and n/2 < p ≤ n, then
     m ≡ ±1 (mod p).
   Then formalize it under lean/ with Lean 4.32 + mathlib. No
   sorry in the main lemma. Add a minimal lakefile stanza for
   this folder if /maths cannot see lean/ otherwise.
2. Re-implement the Berndt–Galway quadratic-residue sieve
   (n dies if some prime p>n has (n!+1 / p) = -1). Run it at
   least through n≤10^4 exactly. Match the three known solutions
   (4,5,7) and no others. If time remains, push the same sieve
   and record *your* bound. Do not quote 10^9 or 10^15 as yours
   unless you ran it.
3. Hunt for obstructions beyond: (i) n≥4 ⇒ m odd; (ii) the
   ±1 lemma above; (iii) a single-prime QR test. Covering
   systems or a modulus family that kills an infinite arithmetic
   progression of n count. Write each as a lemma with a
   human-sized sketch and a computational check on a prefix.
4. If the residue is a covering diagram or a survivor plot,
   save a PNG via /maths/src/maths/figures.py.

Do not claim the Brocard–Ramanujan conjecture. Do not claim a
new Brown number without an independent re-run. Issue #1417 is
already a statement in FormalConjectures; do not spend the
quest re-stating it.

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

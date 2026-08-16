# Quest q1 — Sidon search vs √N + 0.98183 N^{1/4}

- Model: gpt-5.6-sol Max
- Started: (parent fills)
- Status: ready
- Cost: M
- Shape: bound-search

## Idea

Search Sidon subsets of \([N]\) out to at least \(10^4\). Compare
\(|A|\) to \(U(N)=\sqrt{N}+0.98183\,N^{1/4}\). Plot the second-term
gap \(U(N)-|A|\). Try one modular / Singer-style construction that
beats greedy on some \(N\).

## Solve prompt

```
Read PROBLEM.md and this quest file. Attempt only this quest.

Search Sidon subsets of {1,…,N} for N up to at least 10^4.
A set is Sidon if all pairwise sums a+b with a≤b are distinct.

Do this:
1. Greedy: repeatedly insert the least positive integer that
   preserves the Sidon property; restrict to [N]. Record |A|
   for a dense set of N (at least every N, or a fine grid).
2. One modular / Singer-style construction (perfect difference
   set from PG(2,q), Bose–Chowla, or a modular unwrap). Record
   |A| on the N where it applies, and interpolate or pad so it
   can be compared to greedy.
3. Where cheap, compute exact h(N) on a prefix of N (backtrack
   / SAT). Do not spend the quest on a new N^{1/4} coefficient.
4. Plot the second-term gap U(N)−|A| with
   U(N)=√N + 0.98183 N^{1/4}, using /maths/src/maths/figures.py.
   Overlay greedy and the modular family.
5. Exhibit at least one N where the modular/Singer construction
   beats greedy; write both sets down under compute/.
6. Optional Lean: Sidon predicate and a tiny Singer unwrap
   (q=2 or q=3) checked Sidon.

Do not claim a new secondary-term coefficient. Tonight's
benchmark is 0.98183 even if you see later 2026 notes with
smaller published constants.

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

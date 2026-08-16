# Quest q1 — certified small-n cosine minima

- Model: gpt-5.6-sol Max
- Started: (parent fills)
- Status: ready
- Cost: S
- Shape: bound-search

## Idea

For \(n\le 16\), evaluate \(\min_\theta\sum_{a\in A}\cos(2\pi a\theta)\)
on a library of structured \(n\)-sets (intervals, Sidon, Sidon
differences, Bose–Chowla, random) plus a complete search on a small
universe. Plot against \(\sqrt{n}\) and \(n^{1/7}\). Interval-certify
the worst few. The residue is the figure, not a new exponent.

## Solve prompt

```
Read PROBLEM.md and this quest file. Attempt only this quest.

For each n ≤ 16, compute min_θ ∑_{a in A} cos(2π a θ) on structured
n-sets and on a complete search in a small universe.

Do this:
1. Build a library: intervals {1..n} and {0..n-1}; Sidon n-sets and
   Sidon difference sets B−B when |B−B|=n; Bose–Chowla (and Singer
   if the parameters fit); many random n-subsets of a small
   universe. Record the universe for the random samples.
2. Complete search: all n-subsets of {1,…,M} for an M you can
   finish (say M=12 or whatever finishes). Record M.
3. For each (n, family, set) record a numerical min and, for the
   worst few (closest to zero), an interval certificate (mpmath
   balls, or a rational trigonometric identity plus a signed
   evaluation). Dump compute/minima.csv.
4. Plot the recorded minima against √n and against n^{1/7} using
   /maths/src/maths/figures.py. Embed the figure.
5. Optional Lean: Re ∑ exp(2π i a θ) identity and one tiny exact
   evaluation (e.g. A={1,2,3} at a rational θ).

Do not try to improve Bedert's 1/7 exponent. Do not claim Chowla.
Convention: f_A(θ)=∑ cos(2π a θ). Bedert's ∑ cos(a x) on [0,2π]
is the same function.

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

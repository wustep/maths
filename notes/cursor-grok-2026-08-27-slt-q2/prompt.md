You are attacking Simon Lieb–Thirring (2000 #15) on
https://github.com/wustep/maths. Read AGENTS.md and
problems/simon-lieb-thirring/ first (q1 is on this branch / PR #93).
Covering stays frozen. Do not start a new problem.

q1 dent, not independently replayed by Maths: a certified C1 trial
pair gives L_{1,d}/L^{cl} ≤ 1.45576, below FHJN published 1.456
(arXiv:1808.09017 / JEMS 2021). Python 1.455719, Rust 1.455756.
Their Lemma 11 second pair does not convert below 1.456. Sobolev
2/√3 untouched. Conversion L/Lcl = (9√3/4) C1. Replay:
cd problems/simon-lieb-thirring/compute/q1 && ./run_all.sh

This is q2. Orchestrate up to 8 workers on light search, cap
concurrent heavy numeric at 3–4. Aim for a LARGE jump, not another
0.0002 shave.

Targets:
1. Replay q1 first (run_all.sh). If it fails, fix the verifier, do
   not claim 1.45576.
2. Search a better C1 pair / a new test-function class that moves
   L/Lcl by a real amount (toward 1, or at least clearly below 1.45).
   Write the imagined certificate first.
3. Fetch any paper after FHJN that might have already beaten 1.456
   before you claim priority.
4. Dent = verified finite improvement of the published record with
   verifier+cert. Residue if you cannot beat 1.45576.

Update ATTACK.md, WALKTHROUGH.md, PROBLEM.md, README table/ledger.
Open one PR on a q2 branch. If #93 is not yet on main, branch from
this q1 branch and do not fight the merge agent. Rust/C/Python/Lean
as they fit.

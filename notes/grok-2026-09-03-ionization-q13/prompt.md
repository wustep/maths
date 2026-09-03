# Grok 4.6 / 2026-09-03 — Simon ionization excess, q13

Standing goal: produce a novel certified dent on Simon ionization
excess (Simon 2000 #9). Keep attacking until the printed leading
coefficient moves below 1.1010, or useful leftover is honestly
exhausted. Residue wrap only after a real try. Do not merge.

Work only in `/workspace/projects/maths-ion-q13` (branch
`grok/simon-ion-q13`, from origin/main). Repo: wustep/maths.

Printed leading is 1.1010 (q11 / #136):
\(N_c < 1.1010 Z + 3.934 Z^{1/3}\) for \(Z \ge 4\), same HPS chain
(arXiv:2504.18487v1). q12 n=37 face dump is incomplete residue;
predicted 1.1006 is uncertified.

Campaign in `compute/q13/`. Reuse the q11/q12 stack. Prefer
finishing or replacing the n=37 path without a giant dump that
OOMs the machine. Stay RAM-light: ≤2 GB RSS, one heavy job at a
time.

Ledger: update the problem-folder row only (include Grok 4.6 /
2026-09-03). Do not add a q13 ledger line. Do not write “quest”
on README, PROBLEM, or WALKTHROUGH. Do not merge.

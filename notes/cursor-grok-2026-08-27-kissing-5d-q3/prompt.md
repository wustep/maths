Ambitious continuation of five-dimensional kissing on
https://github.com/wustep/maths from current main. Read AGENTS.md
and problems/kissing-5d/.

Main already has q1 (all four 40-point codes polar-maximal; integer
Delsarte excludes 44 on Q5 angles) and q2 (no 41-clique on T5
remainder / half-integer sphere / Q5-cap; unrestricted ansatz duals
≥48; numerical continuum Delsarte ~46.34). Unrestricted range still
40 ≤ τ5 ≤ 44. No unrestricted dual below 44. No 41-point code.

This is NOT a small-dent pass. Hunt a large jump: an exact dual that
excludes some k ∈ {41,42,43,44} on the whole interval [−1,1/2], or a
new exact 41-point spherical code in S⁴. Leftover handles from q2:
36-clique in the 355-point remainder (would give a 41-set via five
universal basis vectors), and the 1480-point (1/4)ℤ⁵ graph. Verify
those yourself; take your own route if better.

Work in compute/q3/. Restricted numerical SDP without exact positivity
is residue. Fetch Tao C29 / Cohn / Mittelmann–Vallentin first. Do not
claim τ5=40 unless you prove it.

House rules: dent = verified new bound with verifier+cert; residue =
incomplete search. README ordinary English, no quest/dent/residue.
Update README only if the unrestricted interval moves. Do not touch
covering or other folders. Open a PR. Report PR URL, whether the
interval moved, replay command, cert paths.

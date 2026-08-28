# Prompts

q26 leftover SAT through n=135 is merged to main as e87139f (PR #137). First remaining hole is now n=136, δ⁺=46.

Stop any further work on the merged q26 branch `cursor/caccetta-q26-n135-bb6b` (that branch was deleted on merge).

Continue the same leftover SAT campaign on a NEW branch from current origin/main (e87139f or later). Do not reuse the merged q26 branch. New leftover stack under `problems/caccetta-haggkvist-k3/compute/q27/`.

Task: leftover exact CH-triangle from n=136. Hunt, store native CaDiCaL DRATs, trim, and independently replay with `verify_range.py` the same way as q26. A wrap is leftover n=136 (or further consecutive leftover orders) stored and independently replayed with 0 failures. Incomplete search at n=136 is residue, not a bound. Do not claim a new unrestricted F₄ unless you actually beat 0.34640 and independently replay that certificate.

Constraints:
- Covering and share/2026-08-16 stay frozen.
- README: add only the q27 leftover row/ledger. Do not rewind later claims already on main (union-closed 0.38305, ionization 1.1013, Caccetta leftover SAT through n=135 / first hole n=136 / F₄ 0.34640, IDS d=4, Hilbert 16(a) ≥ 2,384 with rank ≤21 leftover finished, kissing 40–44, LT 1.44655, Landau 0.22525, Jacobian deg ≥ 125, Sidon 0.94301).
- Open a new PR from the new branch. Title it as leftover SAT from n=136. Keep it a draft scaffold until certs are stored and independently replayed.
- Do not start a different problem.

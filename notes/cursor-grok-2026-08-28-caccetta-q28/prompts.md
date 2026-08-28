# Prompts

q27 wrap merged to main as 2e2e451 (PR #138). Leftover exact CH-triangle SAT through n=136 is on main (43 stored DRATs, independent verify_range 0 failures). First remaining hole is n=137, δ⁺=46.

Continue the same leftover campaign on a NEW branch from current origin/main. Do not reuse the deleted q27 branch. New stack should be problems/caccetta-haggkvist-k3/compute/q28/.

Goals:
- Close leftover n=137 (and keep walking consecutive leftover holes if time allows), store trimmed DRATs, run independent verify_range, update PROBLEM/ATTACK/WALKTHROUGH/CONSTANTS and README (Problems row + ledger only for this leftover).
- F₄ stays 0.34640. Did not beat 0.3388. Incomplete search is residue, not a bound. Do not claim a new unrestricted threshold.
- Covering and share/2026-08-16 stay frozen.
- Keep every later main claim intact in README (union-closed 0.38305; ionization leading 1.1013; Caccetta leftover SAT through the latest certified n after this wrap; IDS d=4; Hilbert 16(a) ≥ 2,384 with rank ≤21 leftover finished; kissing 40–44; LT 1.44655; Landau 0.22525; Jacobian deg ≥ 125; Sidon 0.94301).
- Open a draft PR while hunting; mark ready / undraft only when this wrap has stored certificates + independent replay (or an honest residue wrap with no new bound).
- Replay parent F₄ and q4 CKLS-fork certs still pass; encoder regression still 0 failures.

Ping only if you certify a new unrestricted dent. Otherwise wrap quietly when the next leftover block is closed.

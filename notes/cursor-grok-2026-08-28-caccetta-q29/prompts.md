# Prompts

q28 wrap merged to main as 327f08e (PR #139). Leftover exact CH-triangle SAT through n=137 is on main (44 stored DRATs at d=46, k=46..89; independent verify_range 44 checked, 0 failures). First remaining hole is n=138, δ⁺=46. F₄ stays 0.34640. Did not beat 0.3388.

Continue the same leftover campaign on a NEW branch from current origin/main. Do not reuse the deleted q28 branch. New stack should be problems/caccetta-haggkvist-k3/compute/q29/.

Goals:
- Close leftover n=138 (and keep walking consecutive leftover holes if time allows), store trimmed DRATs after drat-trim -l, run independent verify_range, update PROBLEM/ATTACK/WALKTHROUGH/CONSTANTS and README (Problems row + ledger only for this leftover).
- F₄ stays 0.34640. Did not beat 0.3388. Incomplete search is residue, not a bound. Do not claim a new unrestricted threshold.
- Covering and share/2026-08-16 stay frozen.
- Keep every later main claim intact in README (union-closed 0.38305; ionization leading 1.1013; Caccetta leftover SAT through the latest certified n after this wrap; IDS d=4; Hilbert 16(a) ≥ 2,384 with rank ≤21 leftover finished; kissing 40–44; LT 1.44655; Landau 0.22525; Jacobian deg ≥ 125; Sidon 0.94301).
- Open a draft PR while hunting; mark ready / undraft only when this wrap has stored certificates + independent replay (or an honest residue wrap with no new bound).
- Replay parent F₄ at 0.34645 and the q4 CKLS-fork cert at 0.34640 still pass; encoder regression (including n=21 d=6 SAT and cyclic soundness at n=73 d=24) still 0 failures.

Reuse the q28 encoder/solver/trim/verify stack as the starting point (encode.py is the q1 sequential-counter encoder). High-k cubes empty by the N⁺ counting cut; oversized kissat proofs should be replaced by drat-trim core lemmas that still replay.

Ping only if you certify a new unrestricted dent. Otherwise wrap quietly when the next leftover block is closed.

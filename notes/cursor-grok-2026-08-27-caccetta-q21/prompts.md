# Prompts

q20 is merged to main as #127 / 98074dc. Independent check of certs/keep/replay_129.json: 42/42 ok, every row drat==VERIFIED, k=43..84, n=129, δ⁺=43. First hole is now n=130, δ⁺=44. F4 stays 0.34640. README 3-way kept ionization 1.1017, Hilbert 164/164, kissing 40–44.

Continue leftover SAT on a NEW branch from current origin/main (98074dc or later). Suggested name: cursor/caccetta-q21-n130. Do NOT checkout or push the deleted branch cursor/caccetta-q20-n129-32f8.

Primary: leftover exact cubes at n=130, δ⁺=44, store native CaDiCaL DRATs, replay with verify_range.py --n-min 130 --n-max 130. If that certifies, keep going through consecutive leftover n as far as the VM allows, then wrap the longest certified prefix.

Work in problems/caccetta-haggkvist-k3/compute/q21/. Same layout as q20 (certs/keep/, replay_N.json, summary.json). Scale workers to the VM. Do not launch a RAM-heavy farm past 8 cores / this VM.

F4 hunt below 0.34640 is leftover and not required. Did not beat 0.3388. Conjecture 1/3 stays open.

README / ledger: if you certify through N, print leftover SAT through N and first hole N+1, and keep every claim already on main after #127:
- Caccetta leftover SAT through n=129 (or your new N), F4 0.34640
- ionization leading 1.1017
- kissing 40 ≤ τ5 ≤ 44; type-(2,1) and (1,3) empty
- Hilbert 16(a) ≥ 2,384; rank≤20 leftover thicken 164/164; two (19,3) nests open
- LT CCR 1.44655 (stored 1.45576 is not a dent)
- Landau 3 exponent 0.22525
- Jacobian n=2 max deg ≥ 125
- Sidon r=11 m=48 L=6; union-closed 0.38304
Do not edit covering/ or share/2026-08-16. Open a wrap PR. Do not merge it yourself.

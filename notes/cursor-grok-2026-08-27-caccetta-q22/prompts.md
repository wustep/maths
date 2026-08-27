# Prompts

q21 is merged to main as #129 / 9d12adb. Independent check of certs/keep/replay_130.json: 41/41 ok, every row drat==VERIFIED, k=44..84, n=130, δ⁺=44. First hole is now n=131, δ⁺=44. F4 stays 0.34640. README kept ionization 1.1017.

Continue leftover SAT on a NEW branch from current origin/main (9d12adb or later). Suggested name: cursor/caccetta-q22-n131. Do NOT checkout or push the deleted branch cursor/caccetta-q21-n130-32f8.

Primary: leftover exact cubes at n=131, δ⁺=44, store native CaDiCaL DRATs, replay with verify_range.py --n-min 131 --n-max 131. If that certifies, keep going through consecutive leftover n as far as the VM allows, then wrap the longest certified prefix. You already started an n=131 hunt on q21; that was residue. Resume it on the new branch if the part files are still on the VM, otherwise redo n=131 cleanly.

Work in problems/caccetta-haggkvist-k3/compute/q22/. Same layout as q21. Scale workers to the VM.

F4 hunt below 0.34640 is leftover and not required. Did not beat 0.3388. Conjecture 1/3 stays open.

README / ledger: if you certify through N, print leftover SAT through N and first hole N+1, and keep every claim already on main after #129:
- Caccetta leftover SAT through n=130 (or your new N), F4 0.34640
- ionization leading 1.1017
- kissing 40 ≤ τ5 ≤ 44; type-(2,1) and (1,3) empty
- Hilbert 16(a) ≥ 2,384; rank≤20 leftover thicken 164/164; two (19,3) nests open
- LT CCR 1.44655 (stored 1.45576 is not a dent)
- Landau 3 exponent 0.22525
- Jacobian n=2 max deg ≥ 125
- Sidon r=11 m=48 L=6; union-closed 0.38304
Do not edit covering/ or share/2026-08-16. Open a wrap PR. Do not merge it yourself.

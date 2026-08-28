# Prompts

q22 n=131 wrap is on main (PR #130 merged as 033c0ba). Independent replay: 42/42 DRATs, 0 failures, k=44..85. First remaining hole is n=132.

Continue leftover SAT on a NEW branch from current origin/main. Do not reuse the merged q22 branch.

Leftover: consecutive leftover cubes from n=132. A certified dent is a stored consecutive prefix with `verify_range.py --n-min N --n-max N` reporting 0 failures and every row drat==VERIFIED. Incomplete search is residue, not a lower bound.

Hard constraints:
- Covering and share/2026-08-16 stay frozen.
- Keep every current main claim exactly: leftover SAT through n=131 (first hole n=132), F4 0.34640, union-closed 0.38305, ionization 1.1017, IDS d=4 frontier, kissing 40–44, Hilbert 16(a) ≥ 2,384 with rank ≤21 leftover finished, LT CCR 1.44655, Landau 0.22525, Jacobian deg ≥ 125, Sidon 0.94301.
- README may add only the new leftover folder/ledger line and the Caccetta row if a new consecutive prefix certifies. Do not rewind any other row (especially do not write union 0.38304 or drop IDS / Hilbert rank 21).
- Do not merge. Draft until a wrap.

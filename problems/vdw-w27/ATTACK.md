# Attack log — W(2,7)

## 2026-08-16

- Folder created. Grok 4.6 cloud agent launched.

## 2026-08-16 — residue reconstruction

- Reconstructed the published certificate from quadratic residues modulo $p=617$. Both colors of $0$ give a cyclic 2-coloring of $\mathbb Z/617\mathbb Z$ with longest monochromatic run $6$ and no cyclic 7-AP.
- Six copies color $[3702]$ with no mono 7-AP. One extra bit, forced opposite the $0$-class, colors $[3703]$ with no mono 7-AP. Independent verifier: `python compute/verify_coloring.py compute/coloring_3703.txt`.
- Length $3703$ is the published record, not a dent.

## 2026-08-16 — one-step extension

- Neither color of position $3704$ works on that seed.
  - Color $0$: exactly one 7-AP, the class-$2$ progression of difference $617$: $2,619,1236,1853,2470,3087,3704$.
  - Color $1$: six 7-APs, differences $47,208,236,255,303,332$.
- Single flips of any class-$2$ point create a new 7-AP (difference $285$ at the first point; difference $11$ at the later five). Two-flip follow-up of those new APs: $36$ trials, none clean.
- Cadical, correct at-most-$k$ encoding: $1,2,3,4,6$ flips of the $3703$ seed plus a free last bit are all UNSAT.
- Free tail of width $24,64,128,256,619$ on the same prefix: all UNSAT. In particular the first five QR periods ($3085$ bits) do not extend to length $3704$.
- Min-conflicts from the seed repeatedly stalls at one leftover 7-AP.

## 2026-08-16 — other cyclic templates

- QR scan of every prime $619\le p\le 50000$: no cycle with monochromatic run $\le 6$. Nine primes have run $7$; flipping one or two bits of those $7$-strings never produced a cyclic 7-AP-free coloring.
- Herwig zip without the turn is exactly the $617$ cycle repeated twice. Zip with the turn has complementary halves (so difference-$617$ 7-APs would alternate) but contains a monochromatic $9$-run. CEGAR SAT under the complement constraint plateaued at $\sim 11000$ cyclic 7-APs after $39$ rounds.
- Cyclic CEGAR on $n=618,\dots,622$ timed out with $\sim 2600$ leftover 7-APs each. No cycle longer than $617$ was found.

## Residue

- Best verified coloring: `compute/coloring_3703.txt` (length $3703$, not a dent).
- Best near-miss: `compute/near_3704_color0_one_ap.txt` (length $3704$, exactly one mono 7-AP).
- Verifier: `compute/verify_coloring.py`.
- Search log: `compute/search_summary.json`.
- Do not claim the exact value of $W(2,7)$. The published lower bound is unchanged.

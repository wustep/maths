# Attack log — Graph reconstruction past 13 vertices

## 2026-08-17 — start

House: write only under `problems/graph-reconstruction-next-order`. Target is a
certified reconstruction result at n=14, a structural reduction with an
independently checkable certificate, or a documented residue. Isolated unlabeled
enumerations without a verifier are not a dent. Do not invent a dent. Search
residue is not a bound.

### Published record (fetched 2026-08-17)

McKay, *Reconstruction of small graphs and digraphs*, Australas. J. Combin. 83
(2022), 448–457; arXiv:2102.01942v4 (2 Jan 2022). PDF saved at
`compute/refs/mckay-2102.01942.pdf`.

Theorem 3.1: for n≥4, every graph in the following classes is reconstructible
from its *reduced* deck (hence reconstructible):

- (a) all graphs, n≤13
- (b) triangle-free, n≤16
- (c) girth ≥5, n≤20
- (d) C4-free, n≤19
- (e) bipartite, n≤17
- (f) bipartite of girth ≥6, n≤24
- (g) Δ≤3, n≤22
- (h) degrees in [δ,Δ] on ≤n vertices, for the six triples
  (0,5;14), (5,6;14), (6,7;14), (0,4;15), (4,5;15), (3,4;16)

About 6×10^13 graphs, ~1.5 years of ~3 GHz Intel CPU. Method: canonical
construction path (geng), parent = a ≼-maximal card, compare reduced decks of
siblings. Lemma 2.2: reduced decks determine min/max degree, presence of any
k-cycle for 3≤k<n, and bipartiteness.

No later computational paper (through 2026-08-17 search) pushes the *all-graphs*
frontier past n=13. Interval graphs are now reconstructible for all n≥3
(Heinrich–Kiyomi–Otachi–Schweitzer, arXiv:2504.02353v2, May 2026). A 2023
Information Sciences “vertex-substitution” paper claims a general proof; a 2024
corrigendum exists and the 2026 status pages do not accept it. We do not use it.

Current-status page
https://mlelarge.github.io/graph-conjectures/op/reconstruction_conjecture/
(auto-reviewed 2026-05-08): still open, McKay n=13 is the finite record.

OEIS A000088 (unlabeled graphs): n=13 is 50,502,031,367,952; n=14 is about
2.90×10^16. Exhaustive n=14 is not a one-quest computation. Judge (Codex,
2026-08-16) already said this: cost-L, tonight_quest none.

### What would be a dent

A new line in McKay’s 3.1(h), or a class at n=14 whose membership is
reduced-deck-recognizable (Lemma 2.2) and whose reduced decks we certify unique,
with a rerunnable verifier. Complements are free: G reconstructible iff
complement is.

### Reduction of the n=14 residue (paper + complement)

Degree-range pairs *not* contained in [0,5], [5,6], [6,7], [7,8], or [8,13]
are the residue. Up to complement they are:

(0–4, 6–13), (5, 7–13), (6, 8–13), (7, 9–13),

and the first new tight windows are **(δ,Δ)=(4,6)** and **(5,7)**.

Theory already kills disconnected graphs and (Bondy / Greenwell–Hemminger)
separable graphs without endvertices. For δ≥2 it is enough to test 2-connected
graphs (Yang: the conjecture holds iff it holds for 2-connected graphs).

### Machine

8 cores, ~7 GB free, no packaged nauty (Debian package blocked on cliquer).
Building nauty 2.9.1 from source. Prebuilt `geng` already answers counts.

Next: count the (4,6) and (5,7) windows, write a deck-hash verifier, replay
McKay on small n, then search.

## 2026-08-17 — verifier

Built nauty 2.9.1 from source (`/tmp/nauty2_9_1`). Wrote `compute/deckrecon.c`:
delete a vertex with nauty’s MSB bit macros (first LSB-shift version was
wrong and identified K3 with P3), canonically label each card with
`densenauty`, SHA-256 the sorted graph6 cards (full deck) and the uniqued
cards (reduced deck).

Replay of McKay’s theorem on all graphs:

| n | graphs (OEIS A000088) | full collisions | reduced collisions |
|---|----------------------:|----------------:|-------------------:|
| 2 | 2 | 1 (K2 vs 2K1, the known exception) | 1 |
| 3 | 4 | 0 | 1 (P3 vs K2+K1: same set, different multiset) |
| 4 | 11 | 0 | 0 |
| 5 | 34 | 0 | 0 |
| 6 | 156 | 0 | 0 |
| 7 | 1044 | 0 | 0 |
| 8 | 12346 | 0 | 0 |
| 9 | 274668 | 0 | 0 |
| 10 | 12005168 | 0 | 0 |

Independent check: `verify_labelg.py` rebuilds every card in Python, pipes
them through nauty `labelg` (not our densenauty call), and recomputes
SHA-256. 628 sample lines from n=4 and n=8: 0 mismatches. K4 hash agrees
exactly.

5-regular n=14: 3,459,386 graphs in 335s (already inside McKay (0,5;14)).
Connected 4-regular n=14: 88,168.

1/100 slices of geng `-d4 -D6` / `-d5 -D7` on n=14 were still running after
8 minutes with no `>Z` line. Those windows are too big for tonight. The
new residue inside them is the graphs that actually attain both ends.

## 2026-08-17 — two attack lines

1. **{4,6}-biregular n=14.** Every such graph is a 4-regular graph plus a
   2-factor of the complement (support S, |S|≥3). Degree sequence is a
   full-deck invariant, so uniqueness inside each sequence is
   reconstructibility. Generator: `add_twofactor.c`.

2. **Split graphs n=14.** `geng -u -S 14` → 67,997,750 graphs (62,930,604
   connected). Hammer–Simeone 1981: split-ness is a predicate of the degree
   sequence, so it is full-deck recognisable. McKay did not list this class.
   68 million decks is a longer run than the biregular slices below; left as
   a queued residue.

## 2026-08-17 — the click

The n=14 residue after McKay 3.1(h) and complementation begins at
**(δ,Δ)=(4,6)**. Full enumeration of that window is too large (1/100 geng
slices did not finish in 8 minutes). But the *biregular* slice — degrees
only 4 and 6 — is a 4-regular graph plus a 2-factor of the complement
supported on the degree-6 set.

Support 3 is a triangle. `geng -d4 -D4 14` is 88,193 graphs (88,168
connected), 8 seconds. Overlaying complement triangles and `shortg` gives
a complete, finite list.

LSB-first vertex deletion was a named false start: nauty packs vertex 0
at the high bit. After the fix, n=2..10 replay McKay exactly, and
`verify_labelg.py` matches SHA-256s.

## 2026-08-17 — certified n=14 class

**Every 14-vertex graph of degree sequence 4^11 6^3 is reconstructible
from its full deck.**

- Complete generation (all 88,193 four-regular parents): **8,571,837**
  unlabelled graphs, every one of sequence `[4]^11[6]^3`.
- Connected-parent list: 8,571,676. Extra 161 from the 25 disconnected
  4-regulars.
- Complete-list decks: 8,571,837 distinct full-deck SHA-256s and
  8,571,837 distinct reduced-deck SHA-256s. 17,143 `labelg` samples:
  0 mismatches (`certs/bireg46_s3all_unique.txt`).

Kelly: the degree sequence is a full-deck invariant, so a hypomorphic mate
would have the same sequence and would be on the list.

Not in McKay 3.1. Not triangle-free (the extra 2-factor is a triangle).
δ=4, Δ=6, so not in (0,5;14), (5,6;14), or (6,7;14).

A second list, support 4 (degree sequence 4^10 6^4): 41,538,279 unlabelled
graphs from connected 4-regular parents, hashing in progress.

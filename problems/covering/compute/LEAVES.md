# Covering finite handles

The existing record is in `../PROBLEM.md`. This leaf was reconstructed on
2026-09-10. The current request reopens covering-code constructions beyond
the settled OK37 partition obstruction.

| Leaf | Campaign | Status | Finite handle / outcome |
| --- | --- | --- | --- |
| radius2-r10-n49-block | q9 | residue | Single quotient-block replacements left undecided cases; no 49-column matrix. |
| radius2-r10-n49-aut | q10 | residue | Odd-order exclusions leave the 2-group case; no 49-column matrix. |
| radius2-fibered | q11 | residue | Fibered-family searches leave r=9, n=38 unresolved; no improvement. |
| radius3-ok37-p17 | q12 | residue | Min (3,0)-partition of OK37 is p=18 (Cadical); all p≤17 UNSAT; no dependent triples ⇒ ℓ≥1 impossible. QM_4^3 m=4 needs p≤17 for n=607 — does not apply. |
| radius3-r44-qm43-from817 | q13 | certified | $\ell_2(44,3)\le52351<52415$: the inherited 34-block $(3,0)$-partition and its 65-block refinement cover all $2^{26}$ seed syndromes; the QM$_4^3$ identity is checked column by column. |
| radius3-r41-qm43-merge817 | q16 | certified | Two of 561 block pairs merge validly; the (7,31) merge gives a 33-block $(3,0)$-partition and $\ell_2(41,3)\le26175<26238$ (31 below the notebook's 26206). Full $2^{26}$ seed sweep and independent lift identity check. |
| radius3-r26-delete817 | q16 | blocked | All 817 columns are essential: each occurs in a unique representation of some syndrome, both for the 33-block partition and without block restrictions. No one-column deletion can retain radius 3. |
| radius3-r24-small-seed | q16 | open | Search a new $r=12$ radius-3 seed with a $p\le17$ $(3,0)$-partition and $n\le37$; the settled OK37 seed cannot meet $p\le17$. |
| radius2-r10-n49-two-block | q16 | open | Test simultaneous replacements of two quotient blocks of the certified 50-set, outside q9's single-block replacement family. |

Earlier certified constructions and their replays remain indexed in
`../PROBLEM.md`; their campaign directories predate this leaf.

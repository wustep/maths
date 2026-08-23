# Walkthrough — hadwiger-nelson-plane

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.
Empty beats mean the campaign is not done.

0. What was actually missing — The five-color obstruction in the published
   graphs is already tight. The missing degree of freedom is an additional
   exact unit-distance layer whose constraints cannot all be absorbed by the
   fifth color.
1. Named false starts — A finite patch of one triangular lattice is always
   3-colorable by $(a,b)\mapsto a-b\pmod 3$. A six-color polygonal tiling of
   the whole plane is impossible by Sokolov–Voronov Theorem 2. Neither search
   family can contain the requested object.
2. The useful failure — The tiling theorem separates the two meanings of
   “seven colors”: it closes ordinary polygonal mosaics but says nothing
   against a finite non-5-colorable unit-distance graph. The attack should
   stay on exact finite coordinates.
3. The click — Parts' 509 graph and its ambient algebraic lattice are already
   independently parseable here. Applying the published rotation to the
   entire graph is the cheapest nontrivial test of whether another exact layer
   supplies the missing color pressure.
4. The argument — Rotate every exact point of the Parts graph by
   $\rho=(7+i\sqrt{15})/8$, merge coincidences, and include every unit edge
   found by exact all-pairs comparison. Then try the denser finite reserve
   already enumerated in the same algebraic lattice. A five-coloring of the
   whole reserve union automatically colors every add-only subset, turning
   one SAT model into an exclusion of $2^{677}$ candidate graphs.
5. Computer search —

   | graph | vertices | unit edges | 5-color SAT | independent replay |
   | --- | ---: | ---: | --- | --- |
   | $G\cup\rho G$ | 933 | 4,651 | SAT | exact Python + C coloring check |
   | $G$ plus 677 reserve points | 1,186 | 7,440 | SAT | exact Python + C coloring check |

   The attempt to regenerate the full lattice-disk universe exceeded the
   shared process memory. The finite 677-record source table was therefore
   copied into this folder and each retained exact coordinate was checked;
   the larger enumeration was not claimed as rerun.
6. Proven vs still open — The two committed finite graphs and every add-only
   reserve subset are five-colorable. No six-chromatic finite unit-distance
   graph is proved. Deletions from the base, other coordinates, and the
   heptagonal/Golomb-derived families remain outside this finite exclusion.

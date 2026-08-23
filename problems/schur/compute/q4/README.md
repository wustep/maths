# q4: bounded repairs of the q3 residue

The input is q3's preserved 1,697-vector with exactly the two violations

```
537 + 537 = 1074
537 + 640 = 1177
```

`local_repair.py` first permits the four displayed vertices to change. It
then grows a deterministic neighborhood: a vertex is ranked by how often it
occurs in an immediate blocker to giving one of the four core vertices an
alternative color. All vertices outside the chosen neighborhood remain fixed
to their q3 colors. Every Schur constraint touching a mutable vertex is
encoded exactly; constraints outside are already satisfied by the input.

With Glucose 4.2, the core and the first 16, 32, 64, and 128 ranked blockers
(20, 36, 68, and 132 mutable vertices after adding the core) are all UNSAT.
These are exact walls for those five named neighborhoods only. They do not
rule out a larger repair or an unrestricted 1,697 coloring.

Replay after installing `python-sat`:

```bash
./run_all.sh
```

The preserved `local_repair.json` records the explicit vertex set, clause
count, relevant-edge count, and solver result for every neighborhood. No
1,697 coloring was found in this step.

`scan_templates.py` then checks two finite transforms without SAT:

- all 4,804 swaps between one of the four defect vertices and a vertex of a
  different color; the minimum is 11 violations, attained by swapping 1074
  and 591;
- all 35,616 choices of two color labels and one proper suffix cut, swapping
  those labels for $x$ above the cut. The minimum remains two violations. If
  color 6 is swapped across a cut that separates at least two defect
  vertices, the minimum is 4,361 violations.

The incremental counts for each family's best member are replayed by a fresh
enumeration of all 719,952 Schur pairs. `template_scan.json` preserves the
transforms and exact violation lists. These two scans are also only walls for
their named families. The bound remains
$S(7)\geq1696$.

Finally, `search_shift537.py` tests the named color-twisted translation

$$c(x+537)=c(x)+1\pmod 7.$$

It makes both defects impossible before search:
$c(1074)=c(537)+1$ and $c(1177)=c(640)+1$. Every coloring in the family is
determined by 537 base colors. The exact encoding has 5,031,871 clauses;
19,607 edge/color combinations are automatically safe from the twist.
Glucose 4.2 returns UNSAT, recorded in `shift537_glucose42.json`. Re-running
`run_all.sh` rebuilds the encoding and requires the same UNSAT result. This
rules out only the 537-step color-twisted family and is not an upper bound for
$S(7)$.

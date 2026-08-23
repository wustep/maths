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
1,697 coloring was found in this step, so the bound remains
$S(7)\geq1696$.

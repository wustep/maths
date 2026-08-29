# R(5,5) / q2

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite results

### The complete two-edit ball around the 656

`two_edit_extend.c` checks all
$656\binom{\binom{42}{2}}{2}=242870880$ unordered pairs of edge toggles,
including pairs whose intermediate graph is not a Ramsey graph. Exactly 11136
toggle pairs finish at a $(5,5,42)$-graph. None of those final graphs accepts a
43rd vertex.

The classification pass also explains q1's count of 22000 ordered legal paths:
10864 final pairs have two legal intermediates, 272 have one, and none has zero.
Thus q1 had reached every legal two-edit endpoint, but q2 is the first pass here
that runs the extension test on all of them.

### Prime-order automorphisms on 43 vertices

For an order-$p$ permutation, write $p^c1^f$ for $c$ cycles of length $p$ and
$f=43-pc$ fixed vertices. `orbit_sat.py` emits one clique/independent-set clause
per orbit of 5-subsets and exact weighted degree constraints. Compressed DRAT
proofs, checked by `drat-trim`, exclude

- $11^c1^{43-11c}$ for $c=1,2,3$;
- $13^c1^{43-13c}$ for $c=1,2$;
- $17^c1^{43-17c}$ for $c=1,2$;
- $19^c1^{43-19c}$ for $c=1,2$; and
- $23^11^{20}$.

The degree window $18\le d(v)\le24$ separately excludes
$13^31^4$, $29^11^{14}$, $31^11^{12}$, $37^11^6$, and $41^11^2$.
An order-43 automorphism would make the graph circulant, already excluded by
the parent census. By Cauchy's theorem, a hypothetical $(5,5,43)$-graph
therefore has automorphism-group order with no prime divisor at least 11. This
is a restriction on a hypothetical graph, not a bound on $R(5,5)$.

`verify_encoder.py` exhausts small order-2 and order-7 encodings against the
independent graph verifier. It also exhausts the weighted counter and the
lexicographic symmetry constraint under every small input assignment.

### A certified near-graph ball

The fixed-seed local search found a 43-vertex graph with exactly two bad
5-subsets (5-cliques or independent 5-sets). `bounded_repair.py` encodes the
exact Hamming ball around it: a 5-set too far from monochromatic to be reached
within the radius is omitted, and all other clauses are retained. The checked
DRAT proof shows that no graph within six edge toggles is a $(5,5,43)$-graph.
The near graph is not a Ramsey graph.

## Incomplete searches

The symmetry-broken maximum-cycle instances for orders 2, 3, 5, and 7 were
also run. Any timeout is recorded as `UNKNOWN`; it is not a restriction on
those automorphisms and not a bound. Other cycle types for those primes were
not exhaustively searched.

## Replay

Python scripts that invoke a solver need `python-sat`. The DRAT replay itself
uses pinned source commits and system `gcc`:

```sh
python3 -m venv .venv
.venv/bin/pip install python-sat
PATH="$PWD/.venv/bin:$PATH" ./build_tools.sh
PATH="$PWD/.venv/bin:$PATH" ./verify_proofs.sh
```

The deterministic full replay, including the approximately ten-minute
two-edit extension census, is:

```sh
PATH="$PWD/.venv/bin:$PATH" ./run_all.sh
```

Collected certificate: `certs/q2_summary.json`.

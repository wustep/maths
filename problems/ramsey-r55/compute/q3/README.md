# R(5,5) / q3

No endpoint moved. The published interval remains
$43\le R(5,5)\le 46$.

## Exact finite result: order 7 is excluded

A hypothetical $(5,5,43)$-graph cannot have an automorphism of order 7.
For a permutation of cycle type $7^c 1^{43-7c}$, let $k$ be the number of
7-cycles adjacent to a chosen fixed vertex. The legal degree window is
$18\le d(v)\le24$. Complementing the graph sends $k$ to $c-k$, so the
following representatives cover every degree-feasible value of $k$.

| cycle type | checked $k$ | certificate |
|---|---|---|
| $7^1 1^{36}$ | 1 | DRAT-UNSAT; complementation covers 0 |
| $7^2 1^{29}$ | 1, 2 | DRAT-UNSAT; complementation covers 0 |
| $7^3 1^{22}$ | 1, 3 | DRAT-UNSAT; complementation covers 2 and 0 |
| $7^4 1^{15}$ | 1, 2 | DRAT-UNSAT; complementation covers 3; 0 and 4 violate the degree window |
| $7^5 1^8$ | 2 | DRAT-UNSAT; complementation covers 3; the other values violate the degree window |
| $7^6 1^1$ | 3 | exhaustive 787-case DRUP certificate |

The direct instances reuse `../q2/orbit_sat.py` and its generic cycle/phase
symmetry breaking. Each compressed proof in `certs/proofs/` was checked by
the pinned `drat-trim` build.

The maximum-cycle formula is q2's byte-identical CNF with SHA-256
`b090bb65d208161ea2ac949f976571108baee3dc723a097a8afd05f3b4318206`.
Its unique fixed vertex has degree 21 and is adjacent to three 7-cycles. The
induced 21-vertex neighbourhood has no 4-clique and no independent 5-set.
After q2's symmetry breaking, `p7_neighborhoods.py` exhausts exactly 787
possible assignments to its 30 edge-orbit variables. A checked local DRUP
proves that this list is complete, and a checked DRUP refutes the full q2 CNF
under each assignment. The proofs are packed into eight deterministic tar-gzip
shards; `certs/p7_proofs.json` records every member and archive hash.

By Cauchy's theorem and q2's large-prime exclusions, the order of the
automorphism group of a hypothetical $(5,5,43)$-graph can now have prime
divisors only among 2, 3, and 5. This is a restriction on a hypothetical graph,
not a bound on $R(5,5)$.

## Searches still incomplete

Plain-CDCL reruns of q2's maximum-cycle representatives for orders 2, 3, and
5 returned `UNKNOWN` at five minutes. Other cycle types for those primes are
not exhaustively searched. These timeouts imply no restriction.

## Replay

The Python scripts need `python-sat`. The solver and checker are the pinned q2
builds: kissat 4.0.4 at commit
`8af8e56f174b778aef3aa45af9f739b2a5f492c2` and `drat-trim` at commit
`2e3b2dc0ecf938addbd779d42877b6ed69d9a985`.

```sh
python3 -m venv .venv
.venv/bin/pip install python-sat
../q2/build_tools.sh
./run_all.sh
```

Collected result: `certs/q3_summary.json`. The full replay checks the eight
direct proofs, the local-completion proof, all 787 conquer proofs, archive
hashes, and the regenerated CNF hashes.

# Integer τ table through 50,000

The intended result and its exact verification conditions are in
[CLAIM.md](CLAIM.md). The computation extends the integer-table handle
past q1's endpoint 10,266 and compares the prime counterexamples with
Patanè's September 2026 paper.

## Replay

```bash
bash problems/smale-tau/compute/q3/run_all.sh
```

Dependencies: Python 3 standard library, GCC with OpenMP, and `rustc`.
The driver runs one computational process at a time. It reruns q1's C
and independent Rust exhaustive enumerators through nine steps; the
table bound limits only the output, never the intermediate integers.
Generated binaries and raw counts stay in `.work/`, which is ignored.
No network access is needed to replay.

For each target absent after nine steps, a ten-step program proves the
matching upper bound. `find_witness.c` reuses q1's exact arithmetic and
three-step endgame but stops at the first witness for each target. It
makes no exclusion claim. Python checks all earlier operand pairs;
the separate Rust verifier instead solves for the second operand using
a hash set. Both check lengths and endpoints. Witnesses supplied in the
repository are rechecked, so subsequent replays need not rediscover them.

`replay.py --write` regenerates the certificate and tables. The optional
`--counts C_JSON RUST_JSON` consumes completed census outputs for
development; the default command always reruns both enumerations.

## Why the table is exact

For a positive target, taking absolute values and removing zero or
repeated entries normalizes any shortest program to distinct positive
values without increasing its length. Both enumerators traverse these
programs in the complete pending-queue order described in
[q1's method](../q1/README.md). They use separate implementations and
arbitrary-size integer representations. Their agreement is not a
second proof of the normalization theorem; it checks the implementation
of that common exhaustive-search argument.

The least depth recorded through nine steps is exact. An absent value
has cost at least ten, and an independently replayed ten-step witness
then proves equality. This requires no enumeration of all ten-step
programs. Python trial division and the Rust sieve classify the primes
independently from the completed table.

## Files

| File | Purpose |
| --- | --- |
| `CLAIM.md` | Exact predicate, published comparison, falsifiers |
| `replay.py`, `run_all.sh` | Sequential replay and artifact comparison |
| `find_witness.c` | Upper-bound witness discovery only |
| `verify_witnesses.rs` | Independent witness and prime verifier |
| `tau_table_50000.txt` | Exact costs in OEIS b-file format |
| `prime_counterexamples.csv` | Complete prime list and both costs |
| `witnesses.txt` | Target followed by the values of an optimal program |
| `certificate.json` | Counts and artifact hashes |

The table's maximum cost does not improve A141414's known
initial-interval record. The finite improvement sought here is the
larger complete prime classification. It does not settle a factorial
decision or either form of Smale's conjecture.

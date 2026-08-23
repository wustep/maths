# q2 replay record — 2026-08-23

No bound was proved. The full run ended with `s UNKNOWN`, and the incomplete
search is not evidence for an upper bound.

## Deterministic full instance

Command:

```bash
python3 encode.py --n 33 --k 7 --out es_33_7_signotope.cnf
```

The generator took 29 seconds and produced:

```text
variables       46,376
clauses         5,254,128
bytes           916,030,006
SHA-256         3771831e7d5730d9a2ca81356253cee1c44d5744de92942f664c4767c60f58c9
```

Kissat 4.0.4 ran on this DIMACS file without proof output and with
`--time=300`. It exited 0 after 300 seconds with exactly `s UNKNOWN`. Its RSS
was 1,045,528 KiB at an intermediate 87-second sample. No solver certificate
exists for this run.

## Certificate smoke test

Kissat 4.0.4 returned SAT for `(n,k)=(8,5)` and UNSAT for `(9,5)`.
`drat-trim` independently accepted the text DRAT for `(9,5)` with
`s VERIFIED`; it used 1,589 of 3,150 input clauses and 3,221 of 4,012 lemmas.

```text
n8 CNF SHA-256    ca012f771197fdd43c75dc7a9a0966e2d3cc21b30f73a0ac0574a43ad743418a
n9 CNF SHA-256    a82aaee2281654626dd968d70830c58d51364bd964ed2949afa298f5c0ee7852
n9 DRAT SHA-256   d975f6fce8a259f1718feb093ccfa6b75316393b09f349d0de6f7136ebef328c
```

The source archive used to build Kissat had SHA-256
`c4ec54f5034ec096a2ce0dbb38ecd235e673c999d7073c771dcc21c4f32fc123`.
The resulting Kissat binary had SHA-256
`0e0470d5ef16740554ad2453183546067b190d85b82d17bbfad6c6a7bc76cb49`;
it reports GCC 14.2.0 with `-O3 -DNDEBUG -DQUIET` and an unknown git ID.
The locally built `drat-trim` binary had SHA-256
`7d426a913ba22202174cb3a57ef9924b28c62b90a65bcaffa7e010281116c6bb`.
These binaries are not notebook artifacts; `run_all.sh` accepts independently
installed copies through `KISSAT` and `DRAT_TRIM`.

## ES(6) storage wall

The same encoding returned SAT for `(16,6)`. A proof-producing `(17,6)` run
was manually stopped after 2 minutes 53 seconds with no answer. Its incomplete
text DRAT had reached 586,153,984 bytes and cannot be checked as a proof. The
uncommitted CNFs had these deterministic hashes:

```text
n16 CNF SHA-256   4983a9cc8c2f1a0219f4428a4d5d6c0a0f0ef77936ce2c4722011c7308e3bb75
n17 CNF SHA-256   0e3ed27cf6c6ab316df344674fb834761d219b7e9e349c00326d0ff0f9db9a3f
```

This wall is why the full 33-vertex reconnaissance did not request a proof.
An UNSAT claim at 33 would require a new proof-producing run and independent
verification; the bounded run above made no such claim.

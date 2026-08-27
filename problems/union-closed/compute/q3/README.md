# q3 — certify the fifth decimal on the `{b,1}` ray

Pure Liu Example 4 certifies frequency `0.38305` on `{b,1}`.  Thus

    0.38305 > 0.38304 > 0.382709087918741.

The first inequality improves the q1 ray record.  The second compares
with Liu's published Example 5 number.  The analytic first-crossing is
unchanged:

    0.3830513565868255825….

The printed constant is `1.3565868e-6` below that crossing.  A
9,000 by 7,000 mesh checks every retained point with mean at most
`0.38305`.  The Python verifier uses monotonicity to inspect the last
retained point in each row; the C verifier independently visits every
retained point in the 63,000,000-point grid.  Their retained-cell
counts, minimum ratios, and minimizers agree.  The mesh minimum is
`1.0000049143029008`, recorded in
`certs/certificate.json`.

Replay:

```sh
PY=/path/to/python ./run_all.sh
```

Python needs `mpmath`; the mesh and comparison use the standard
library.  `run_all.sh` also compiles `verify.c` with `gcc -O3`.

`probe_joint.py` records a failed route past the q2 ceiling.  For
independent bits, the shared-union pair `(A union B, A union C)` already
has an interior entropy equality near `0.343708`, so that joint-output
inequality is weaker than the current ray protocol.

The scope is the `{b,1}` hypothesis class used in q1 and Liu's
numerical optimizer.  Frankl's `1/2` target and the every-measure
inequality remain open.

## Acknowledgements

Codex (GPT-5) ran the q3 search and certificate.  Stephen Wu is the
human author of the notebook.

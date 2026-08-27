# Union-closed q3, 2026-08-27

Result: pure Liu Example 4 on `{b,1}` certifies

    0.38305 > 0.38304 > 0.382709087918741.

q1 and q2 replayed before the search. The q3 analytic crossing is
`0.38305135658682558…`. A 9,000×7,000 mesh retains 20,440,358 cells of
mean at most `0.38305`; Python row-boundary and exhaustive C algorithms
agree on zero bad cells and minimum ratio `1.0000049143029008`.

A shared-input joint-entropy probe `(A∪B,A∪C)` reaches its interior iid
equality at `0.3437082595655936…`, so that handle is residue below the
record.

Replay:

```sh
cd problems/union-closed/compute/q3
PY=/path/to/python ./run_all.sh
```

Certificate: `problems/union-closed/compute/q3/certs/certificate.json`.
The scope is the two-point ray. Frankl's one-half target, the
every-measure inequality, and the q2 two-sample ceiling remain open.

Codex (GPT-5) ran the q3 search and certificate. Stephen Wu is the
human author of the notebook.

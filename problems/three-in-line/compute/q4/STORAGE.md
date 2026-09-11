# DIMACS storage

`n75-rct4.cnf` (~41 MB) is not in the git tree. The committed
record is `n75-rct4-audit.json` (SHA-256
`1709cdf478920fd9ed0160bc5f00e049b10f0f6b28a1955560cd4aaa88205317`,
996434 variables, 2398895 clauses).

## Regenerate

Needs `python-sat`. From this folder:

```
python3 ../search_sat.py --n 75 --write-cnf n75-rct4.cnf --seconds 0.01
python3 ../audit_dimacs.py n75-rct4.cnf --json /tmp/n75-rct4-audit.json
```

`search_sat.py` also starts a solver; the `--seconds` cap is only
to exit after the DIMACS write. Compare the audit SHA-256 to
`n75-rct4-audit.json`. `run_all.sh` audits the CNF only when the
file is present locally.

No proof trace was stored for the near-seed UNSAT runs; those JSON
files remain residue, not a certified exclusion.

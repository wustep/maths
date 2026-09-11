# SAT proof storage

Compressed DRAT proofs and the q3 cube-shard tarballs are not in
the git tree. The committed record is the JSON under each
`q*/certs/` folder (`q2_summary.json`, `p7_proofs.json`,
neighborhood lists, orbit metadata).

## Regenerate

Encoders:

- q2 orbits: `q2/orbit_sat.py --n 43 --p P --cycles C --cnf …`
- q2 repair ball: `q2/bounded_repair.py certs/local_best2.g6 6 --no-solve --cnf …`
- q3 order-7: `q3/verify_direct_p7.py` / `q3/verify_p7_proofs.py` (see that folder’s README)
- q4–q6 order-5: the `run_all.sh` in each folder, once proofs are local

Solvers and `drat-trim` are the pinned q2 builds (`q2/build_tools.sh`).
Re-solving is not scripted to a single one-shot command for every
cube; the READMEs name the instance. There is no Release URL for
the old proof blobs.

`local_best2.g6` (153 bytes) and `refs/r55_42some.g6` stay in the
tree: those are graph witnesses, not proof dumps.

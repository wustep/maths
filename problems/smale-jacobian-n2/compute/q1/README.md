# q1 — exclude the exceptional degree pair

Guccione–Guccione–Horruitiner–Valqui, Theorem 2.1, leaves one degree
pair below 125: \((72,108)\), up to transposition. Their Proposition 4.3
reduces it to two explicit Laurent systems. Helali's archive gives exact
unit-ideal certificates for both systems.

`certificate.json` is the local certificate manifest. It records the published
polygons, the degree implication, the immutable source commit, the whole-archive
SHA-256, hashes of the central exact identities and verifiers, and every
required terminal marker. The 86 MB blob is not duplicated in Git; its hash
binds the remote Zenodo/Git artifact byte for byte.

Before invoking the large certificate, `run_all.sh` checks the bridge twice:

1. Python and Rust independently enumerate every lattice point in both pairs
   of polygons.
2. Both expand the five Laurent coefficient identities from the chain rule.
3. Both check the coordinate change and the nonsingular normalization matrix.
4. Their complete outputs must agree byte for byte.

The script then hashes and safely extracts the pinned archive, checks eight
central internal files, and runs the archive's complete characteristic-zero
replay. It requires `curl`, `rustc`, Python with virtual environments, and
network access on the first run.

```bash
cd problems/smale-jacobian-n2/compute/q1
./run_all.sh
```

For an already downloaded archive and prepared Python environment:

```bash
JC2_72_108_ARCHIVE=/path/to/jc2_72_108_exact_replay_v1.0.1.zip \
JC2_72_108_PYTHON=/path/to/venv/bin/python \
./run_all.sh
```

The final marker is `Q1_DEGREE_125_CERTIFICATE_PASS`. The result excludes the
finite \((72,108)\) exception; it does not prove the plane Jacobian conjecture.


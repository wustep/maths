# Independent certification of the 0.1787854 candidate

The complete certificate establishes
$\Lambda\leq893927/5000000=0.1787854<1/5$;
[`CLAIM.md`](CLAIM.md) states the exact inequality and falsifier.
Both complete finite implementations, all fresh analytic lanes, and the
independent certificate assembly have passed.

The candidate is due to Jude Gomila. This folder adds a new complete finite
algorithm and an analytic audit. [`NOTE.md`](NOTE.md) develops the argument,
[`INTERPOLATION.md`](INTERPOLATION.md) proves the new finite remainder bound,
and [`ANALYTIC_REVIEW.md`](ANALYTIC_REVIEW.md) records the review of the
candidate's analytic transfers. See [`ATTRIBUTION.md`](ATTRIBUTION.md) for
source and authorship boundaries.

## Reproduction

The pinned upstream checkout is required because the analytic source and
archived comparison data remain there:

```bash
git clone https://github.com/judegomila/dbn-lambda-01787854-candidate-audit.git candidate
git -C candidate checkout a74738deb6d5e0f76887cb36901da08b68dca705
```

This checks both entire retained finite
streams, all coefficient containments, all 883 prism inequalities, and the
analytic interfaces. It requires Python 3.11 or later and git:

```bash
bash problems/riemann-hypothesis/compute/q2/run_all.sh "$PWD/candidate"
```

This mode checks the recorded interval computations. To rebuild the
programs and regenerate all numerical lanes, supply a **new** output
directory:

```bash
bash problems/riemann-hypothesis/compute/q2/run_all.sh "$PWD/candidate" /tmp/rh-q2-new-run
```

The fresh mode additionally requires a C17 compiler, 64-bit Unix, Rust,
FLINT 3 with its Arb headers, and Python packages `mpmath`, `sympy`, and
`python-flint`. The completed finite run used GCC 14.2.0, Rust 1.85.0,
FLINT 3.1.3, mpmath 1.4.1, SymPy 1.12, and python-flint 0.9.0.
Activate the Python environment before running. For a non-system FLINT
installation, export `FLINT_PREFIX` to its prefix containing `include/`
and `lib/` or `lib/x86_64-linux-gnu/`.

Fresh mode runs one numerical process at a time. Do not start a second
fresh run alongside it. Logs are streamed and complete finite outputs
occupy about 213 MB before compression. The two finite computations used
less than 18 MiB each including their launchers. The historical upstream
stored assembly was also checked once, but it buffered about 1 GB; it is
excluded from the normal reproduction path because the new stream checks
replace it. The reported RSS in its old lane manifest is cumulative
across children and must not be read as each later job's memory usage.

## What is checked independently

| Obligation | First check | Independent check and scope |
| --- | --- | --- |
| Every finite index | Original C Taylor producer | Rust positive-sum interpolation over all 3,149,013 indices; shares Arb |
| Weakest finite index | Original C row | Rust direct convolution without interpolation |
| Finite implementation regression | Rust update/merge algorithm | Python dictionary convolution on 100 cases |
| Finite error and infinite tail | Fresh C/Arb enclosures | Python interval calculations; repeated C precision is additional corroboration |
| Barrier | Fresh coefficient, remainder, derivative, and winding computations | Independent rational parser for all coefficient containments, seams, winding intervals, and prism inequalities |
| Theorem transfer | Candidate's supplied argument | Source-level analytic review, including the zero-time endpoint; no external human review claimed |

`check_rejections.py` tests 16 malformed-certificate cases, including a
wrong finite row with its hash updated to match. Hashes identify the
evidence; the content checks enforce coverage and decisive inequalities.

## Files

- `vendor/finite_original.c`, `regenerate.py`: original producer and full
  streaming replay against the pinned archives.
- `direct.rs`, `interpolate.rs`, `ball.rs`, `arb_bridge.c`: independent
  finite algorithms. The C bridge provides Arb operations only.
- `check_small.py`, `check_rejections.py`: mathematical regression and
  certificate rejection checks.
- `replay_analytic.py`: fresh height, error, tail, and barrier runs.
- `verify_finite.py`, `verify_analytic.py`: complete transcript checks.
- `archive_results.py`, `check_certificate.py`: retention and replay of
  complete evidence. Lane manifests retain `claim_certified: false` or
  `certifies_claim: false` because an individual lane is insufficient.

The complete compressed certificate occupies about 47 MiB. The
[`finite-floor figure`](figures/finite-floors.svg),
[`PDF`](figures/finite-floors.pdf), and
[`exact bin data`](figures/finite-floors.csv) show the two verified floors;
the drawing is not a proof input.

An incomplete range, nonpositive margin, failed interval comparison,
altered numerical source, missing analytic input, or unfinished barrier
prevents success. A successful diagnostic is not the bound in `CLAIM.md`.

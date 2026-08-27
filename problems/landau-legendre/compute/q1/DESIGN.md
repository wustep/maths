# q1 design

## Caller contract

```bash
problems/landau-legendre/compute/q1/run_all.sh
```

The command is network-free, resolves every path relative to itself, builds in
a temporary directory, and leaves the checkout unchanged. A caller with a
local clone of the OLC repository can additionally authenticate the public-log
projection:

```bash
problems/landau-legendre/compute/q1/replay_olc.sh /path/to/olc
```

## Modules and evidence boundaries

- `make_rh_certificate.py` creates exact rational logarithm enclosures.
  `verify_rh_certificate.py` independently reconstructs them, and
  `verify_rh_float.c` checks the two signs through a separate `long double`
  implementation. The exact Python check is authoritative. The surrounding
  theorem still cites the RH interval theorem and the published finite
  Oppermann computation.
- `audit_olc.py` reads tracked Git blobs from a pinned upstream commit. It
  projects cumulative worker rows into `certs/olc_rows.tsv.gz` and records
  their provenance and union coverage in `certs/olc_public_audit.json`.
  `verify_olc_audit.py` can check the projection offline. Only
  `replay_olc.sh` authenticates it against upstream.
- `generate_edge.rs` finds the least prime in both Oppermann halves for the
  last 100,000 square intervals below $2^{64}$. `verify_edge.py` independently
  rechecks every earlier candidate with the first twelve prime
  Miller--Rabin bases. `make_edge_summary.py` derives the certificate hash and
  exact near-miss rankings.

## Invariants

1. The RH constants reduce to
   $\alpha=8901/4000$, $\delta/\alpha=901/8901$, and
   $44/(25\alpha)=7040/8901$.
2. The exact overlap margin and the derivative margin are positive. The
   analytic side includes the splice point; the finite side covers the strict
   complement.
3. OLC selects only tracked blobs matching
   `^(bigdawg|phi)/data[^/]*/[^/]+\.out$`. Counters are differenced in file
   order. A nonzero upstream `countfails` means a fallback was used, not that
   an Oppermann interval failed.
4. OLC coverage is the union of completed half-open integer ranges. Its four
   public-log holes are residue and do not revise the paper's result.
5. Slice endpoints use 128-bit or arbitrary-precision arithmetic. Every
   witness is strictly inside its half, prime, and the least prime after the
   left endpoint. Rankings compare exact offset-to-width ratios.

This design uses the stronger evidence boundary from arena candidate A, with
candidate B's reduced constants, splice checklist, standard-library C
diagnostic, and stricter parser accounting.

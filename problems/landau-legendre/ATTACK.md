# Attack log: Landau 3 / Legendre

Chronological attempts, newest last.

## 2026-08-27: record correction before search

The starting note said the computational record was $2^{64}$. The published
record is much larger. Sorenson and Webster verified the stronger Oppermann
conjecture through $n=7.05\cdot10^{13}$, which checks square-height
$n^2=4.97025\cdot10^{27}$. A finite search near $2^{64}$ can be an independent
replay, but it cannot move the record.

The proposed prime-gap formulation also needed correction. The inequality
$p_{k+1}-p_k<2\sqrt{p_k}$ is sufficient for Legendre, not equivalent to it.
The exact finite predicate is that no interval between consecutive integer
squares is prime-free.

## Ten imagined end-states

These were written before implementation. Each is a concrete artifact that
would improve, replay, or sharpen a documented result.

1. **RH exponent $0.22525$.** A rational-arithmetic certificate proves that
   the Chamberland--Straub overlap works for
   $\delta=901/4000=0.22525$, improving their printed $0.2253$.
   It might work because their value is rounded; it might die if the exact
   overlap or real-$x$ endpoint uses hidden slack in the other direction.
2. **One new Oppermann chunk.** Certify both half-intervals for every $n$ in
   a nonempty interval immediately beyond $7.05\cdot10^{13}$.
   It might work with their arithmetic-progression code; it might die on
   compute cost or unavailable production parameters.
3. **Published endpoint replay.** Recover the final checked Sorenson--Webster
   shard and independently validate its row counts and primality evidence.
   It might work if the repository contains the production logs; it might die
   if only a partial upload is public.
4. **Public-log coverage certificate.** Canonicalize every checked-in OLC log
   row, identify overlaps and holes, and certify the exact union of public
   intervals. It might expose a replayable documented slice; it might die as
   residue if the public logs do not reach the paper's endpoint.
5. **Top-of-$2^{64}$ Oppermann slice.** Give two prime witnesses for each of
   the final $100{,}000$ square intervals below $2^{64}$ and verify them with
   an implementation independent of the generator. It might work because
   deterministic 64-bit primality testing is cheap; it cannot beat the modern
   record.
6. **Near-miss table at the same edge.** Rank the largest least-prime offsets
   in each Oppermann half over that $100{,}000$-interval slice, with every row
   recoverable from the witness certificate. It might reveal a useful stress
   case; it might die as merely typical data.
7. **Prime-gap-table replay through $10^{20}$.** Hash and independently scan
   the current exhaustive gap data, deriving its exact Legendre prefix.
   It might give a clean provenance bridge; it cannot catch the published
   Oppermann record.
8. **Explicit unconditional $x_0$.** Extract all constants in the
   Baker--Harman--Pintz argument and certify an explicit threshold for some
   $\alpha<2.106$. It might turn an effective theorem into a finite statement;
   it might die because the paper explicitly leaves the constant extraction
   as substantial work.
9. **Smaller-power exception extension.** Extend and certify the OEIS list of
   prime-free intervals $[n^{3/2},(n+1)^{3/2}]$ far past its published search.
   It might be cheap and informative; it might not say anything new about
   exponent $2$.
10. **Almost-prime bridge extension.** Extend Campbell's explicit
    $\Omega\leq3$ square-interval range past $n^2=10^{31}$ with a checked
    multiplier and current gap bound. It might work by retuning one prime;
    it might remain adjacent to, rather than progress on, Legendre.

## Pick three, then prune

The ranking criterion was published-record delta times checkability in one
session.

1. **Conditional exponent tightening:** small but genuine theorem delta, and
   the only numerical step is an exact one-variable inequality.
2. **Public OLC coverage audit:** potentially reaches the published endpoint,
   and immediately says what the available evidence can actually replay.
3. **$2^{64}$-edge slice plus near-miss table:** no modern record delta, but
   fully checkable and supplies the requested independent fallback.

Items 2, 7, 8, 9, and 10 above were pruned on compute cost, missing source
artifacts, or distance from Legendre. Item 3 was folded into the public-data
audit, and item 6 was folded into the deterministic slice. No work starts on
the pruned lines.

## Certificates imagined before code

### A. Conditional exponent

`certs/rh_delta.json` will contain $N$, the rational $\delta=901/4000$, the
paper's overlap inequality, rational lower and upper bounds for every
logarithm, and a positive rational lower bound for

$$
F(\delta)=\frac{\delta}{2+\delta}\log N
-\log\!\left(\frac{44\log N}{25(2+\delta)}\right).
$$

The verifier must reconstruct the logarithm enclosures from rational series,
not trust decimal strings in the certificate.

### B. Public OLC data

`certs/olc_public_audit.json` will pin an upstream commit and list the number
of parsed rows, unique starts, duplicates, covered endpoints, holes, and row
invariant failures. A verifier will reparse a local clone when supplied. The
committed certificate alone records provenance; it does not turn missing logs
into a published-range replay.

### C. Deterministic edge slice

`certs/edge_witnesses.csv` will have one row for every
$n\in[2^{32}-100000,2^{32}-1]$ and the least prime in each open Oppermann
half. `certs/edge_summary.json` will pin the range, row hash, maxima, and the
largest normalized least-prime offsets. The generator and verifier will use
different deterministic Miller--Rabin base sets and separate source files.

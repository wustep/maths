# Attack log — Riemann hypothesis

Chronological attempts, newest last.

## 2026-08-30 — establish the record

- Read the Clay statement and the Hilbert, Smale, Millennium, and Landau
  catalogs. This is Hilbert 8(a), Smale 1, and a Clay problem. The existing
  Landau 3 folder is an RH-conditional consequence, so it is cross-linked
  rather than duplicated.
- Fetched Rodgers–Tao arXiv:1801.05914 and Polymath 15 arXiv:1904.12438 with
  `scripts/arxiv_fetch.py` before using their constants.
- The supplied Platt–Trudgian identifier, arXiv:2007.02194, resolves to a
  software-refactoring survey. Logged that failed lookup, found the correct
  primary source at arXiv:2004.09765, and fetched it with the same script.
- Record fixed at $0\leq\Lambda\leq0.2$: Rodgers–Tao prove the lower endpoint;
  Platt–Trudgian prove RH through height $3{,}000{,}175{,}332{,}800$ and state
  the $0.2$ consequence of Polymath 15.

## 2026-08-30 — replay the published upper-bound parameters

- Polymath 15 Theorem 1.2 yields $\Lambda\leq t_0+y_0^2/2$ once its height,
  asymptotic-region, and barrier hypotheses are all established.
- Its Table 1 second row prints $X=5{,}000{,}000{,}194{,}858$,
  $t_0=0.186$, and $y_0=0.16733$. Exact arithmetic on those strings gives
  $0.19999966445$. The Platt–Trudgian height exceeds $X/2$ by
  $500{,}175{,}235{,}371$.
- The table entries are rounded. Neither paper proves that the displayed
  digits retain all three hypotheses at $0.19999966445$, so this calculation
  is a replay diagnostic and no dent.

## 2026-08-30 — audit the off-arXiv 0.1787854 lead

- Pinned
  [`judegomila/dbn-lambda-01787854-candidate-audit`](https://github.com/judegomila/dbn-lambda-01787854-candidate-audit)
  at commit `a74738deb6d5e0f76887cb36901da08b68dca705`. The repository describes
  itself as a candidate audit outside peer review and arXiv, so it is a lead
  rather than the record.
- Replayed the exact identity

  $$
  \frac{129}{800}+\frac12\frac{87677}{2500000}
  =\frac{893927}{5000000}=0.1787854.
  $$

  Its $X=6{,}000{,}000{,}185{,}827$ requires RH through $X/2$; the published
  Platt–Trudgian height clears that input by $350{,}479{,}773/2$.
- Ran the complete stored review. Its seal covered 443 files. The verifier
  parsed every stored finite row $N=690988,\ldots,3840000$ (3,149,013 rows),
  found no gap, overlap, or uncertain row, and obtained stored finite floor
  $7.91366\cdot10^{-7}$ against error upper
  $2.33494905212337849\cdot10^{-7}$. The stored tail, barrier, sign map, and
  exact criterion checks also passed.
- Kept the machine to one compute job at a time. Fresh FLINT/Arb runs at 256
  and 512 bits reproduced the Proposition 4.10 error majorant with margin
  greater than $5.57871094787662\cdot10^{-7}$ and the infinite-tail
  contraction with margin greater than $1.73520937333\cdot10^{-4}$.
- Regenerated the barrier sequentially. All 7,688 regenerated components fit
  their stored interval balls. The uniform error was below
  $0.000356523012<0.00125$; 883 consecutive time prisms covered
  $[0,0.16125]$, the winding integer was zero, and the minimum printed prism
  margin exceeded $0.5198$. Fresh logs and hashes are retained in
  `compute/q1/fresh/`.
- Compiled the finite producer from source hash
  `580d0b51165da58d4ca22e16d80a8c3db603dd0d9246f26dd027b5f820bf0808`
  with GCC 14 and FLINT 3.1.3, then regenerated the first row on one
  low-priority core. At $N=690988$ its canonical output
  `L12 0.000000791366 GT089 0` matches the sealed row exactly. The run took
  242 seconds and about 5 MB RSS.
- The full expensive finite-row producer was not rerun: its archived shards
  were fully parsed, while the upstream full regeneration uses a parallel
  workflow during the existing Hilbert 16(a) search. The analytic bridge,
  including the
  explicit $t=0$ scope note in the candidate's own uniform-error verifier,
  was not independently proved here. Thus $0.1787854$ remains residue. The
  published upper endpoint stays $0.2$.

## 2026-08-30 — replay a published Lehmer pair

- The Saouter–Gourdon–Demichel paper has no arXiv version located in this
  search, so fetched its official AMS journal PDF. A guessed arXiv identifier
  0809.1846 was unrelated and is logged in `RESEARCH.md`.
- Recomputed the paper's displayed four zero ordinates and Theorem A formula.
  The Python path gives

  $$
  G=379.1994713627945\ldots,\qquad
  \delta^2G=3.47470927295\ldots\cdot10^{-8},
  $$

  and

  $$
  \lambda_k=-1.14540945809\ldots\cdot10^{-11},
  $$

  reproducing the printed historical bound
  $\Lambda>-1.14541\cdot10^{-11}$. An independent C calculation checks broad
  corridors for all three values.
- This route has no present lower-bound headroom because Rodgers–Tao proved
  $\Lambda\geq0$. The replay is useful as a small certificate, but no dent.

## Leftover

- Extend the one-row fresh producer check to all 3,149,013 finite rows under a
  separately implemented interval program, then compare the complete row
  stream rather than trusting archived shards.
- Audit each analytic implication from the numerical inequalities to the
  Polymath 15 hypotheses, especially the $t=0$ transition and the barrier's
  normalization and zero-count transfer.
- If the candidate appears on arXiv, replay that version from a clean source
  tree and compare its statement and hashes with this pinned lead.

# Walkthrough — simon-lieb-thirring

Discovery notes, not a cleaned proof. Beats: `refs/walkthrough-style.md`.
Empty beats mean the search is not done.

0. What was actually missing — The published upper bound on L(1,d),
   stated as a theorem in a paper, not a wiki number. Simon's #15 is
   the one-dimensional slot 1/2 < γ < 3/2. The finite object that
   can move is that ratio, currently 1.456.

1. Named false starts — Treat arXiv:2203.06051 as a Frank survey.
   The id is Schimmer; Frank's survey is 2007.09326. Both quote
   the same 1.456, so the record does not change, but the author
   line does.

2. The useful failure — Wikipedia states Simon #6 as AC spectrum
   at coupling 2. The 2000 reprint says coupling strictly less
   than 2. That is a warning to read the reprint before copying
   a table, including for #15's (γ,d) range.

3. The click — Frank–Hundertmark–Jex–Nam Theorem 1 is the number
   to beat. Schimmer and Frank still call the 1/2 < γ < 3/2 slot
   open in 2020–2022. No later improvement turned up this session.

4. The argument — None. The classical constant and the sech²
   ratios are checks, not an attack on 1.456.

5. Computer search — `compute/lt_constants.py` rebuilds Lcl from
   the Gamma formula, checks 2/(3π) and 3/16, records 2/√3 and
   1.456, and evaluates sech² witnesses. See `compute/record.json`.

6. Proven vs still open — Replayed the published record. Did not
   beat 1.456. Simon #15 remains open.

# Ionization: finish the 40-bin calculation

GPT-6 Astra, 2026-09-20. Work is in
[`compute/q16/`](../../problems/simon-ionization-excess/compute/q16/).

The target is leading coefficient 1.1 on the q14 range, with the
same 3.933 remainder. No new bound is certified yet. Both q14
verifiers passed before search. Run one SDP at a time with one
numerical thread and a memory limit; independently verify before
updating any bound.

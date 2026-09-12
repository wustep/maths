# Unfinished 40-bin ionization calculation

No improvement was certified. The bound remains

$$
N_c(Z)<1.1005Z+3.933Z^{1/3}\qquad(Z\ge4).
$$

Both q14 verifiers passed during this run. The new proposal was to
use 40 rational bins at aspect ten and target 0.9124, aiming for
the existing mass-stationary cutoff 10/11. No SDP search ran and
no new witness was produced before the midnight stop.

[CLAIM.md](CLAIM.md) preserves the unproved target and its falsifier.
`bash run_all.sh` exits 2 because certification is incomplete.
The q14 certificate remains independently replayable with
`bash ../q14/run_all.sh`. No usage-limit resets were used.

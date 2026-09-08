# Riemann hypothesis: independent verification campaign

The target is $\Lambda\leq893927/5000000=0.1787854$, compared with the
published Platt–Trudgian upper bound $1/5$. The number and candidate
construction are due to Jude Gomila. This campaign is completing the
finite regeneration and analytic review left by the earlier notebook run.
The fresh barrier is still running; the bound is not yet asserted.

Work lives in
[`compute/q2/`](../../problems/riemann-hypothesis/compute/q2/).
The model is GPT-6 Astra, 2026-09-08. The exact user prompt is preserved
in [`prompt.md`](prompt.md). No other problem's claim was changed and
covering was left untouched.

Both complete finite calculations have finished. The original C program
regenerated all 3,149,013 rows in 23 sequential segments and matched the
candidate archives exactly. A new Rust algorithm interpolates positive
Dirichlet sums at eight nodes, with a proved derivative remainder and exact
cutoff updates. It independently checks every index and reaches the same
minimum floor $791366/10^{12}$ at $N=690988$. The C run took 4265.578 seconds;
the Rust interpolation runs took 600.144 seconds. A separate Rust direct
convolution at the weakest row took 73.064 seconds.

The finite error allowance is
$233494905212337849/10^{24}$, leaving the exact margin
$557871094787662151/10^{24}>0$. Python dictionary convolutions checked
100 small cases. Sixteen deliberate certificate corruptions were rejected,
including corruptions with matching updated hashes.

The analytic review reads the pinned source against the actual published
theorems. It checks the native convolution's normalization and conjugation,
the Dini derivative at coefficient zeros, all-window and all-height
directions, cap monotonicity in the infinite tail, and the barrier homotopy.
It supplies the compact dominated-convergence argument needed to include
$t=0$. The coefficient generator's old quadrature is used only to select a
matrix size; the separate factorial remainder is the required proof of
truncation accuracy.

Fresh C/Arb error and tail runs at 256 and 512 bits have passed, as have
the 180/256-bit height-transfer runs, the correction/normalizer checks,
and the Python interval tail. The whole barrier has been queued and is
regenerating its coefficient matrix and closed-prism cover.

The two main finite programs use little memory and ran sequentially under
an exclusive lock. The historical stored assembly unexpectedly buffered
about 1 GB; it passed after a compiler include-path repair, and was then
removed from the normal replay path. Its work is redundant with the new
streaming certificate assembly. Dependency installation remained under
`/tmp`; package downloads and the upstream clone used the granted network
approvals. No publication, merge, or external mathematical endorsement is
implied by the local computations.

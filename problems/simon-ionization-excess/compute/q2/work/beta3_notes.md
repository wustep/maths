# β_3^{rad} — residue, not a dent of 1.1185

Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1, Proposition 4.5:
β_3 ≥ min_t f(t) = 1/b(3) ≈ 0.894107, with f(t)=(1+t^3)/(1+t^2) and
b(3)<1.1185. Figure 2 says this is not sharp: power-law trials sit
about 3% below b(3). A certified γ > 1/b(3) that holds for every
radial probability in (4.1) would be a new leading coefficient in
the same §5–§7 chain.

Status: residue. The printed leading coefficient 1.1185 is unchanged.

## Numerical target (upper bounds on β_3)

Replay: `explore_beta3.py`. Wrong direction for an ionization *upper*
bound.

- Power law m(dr) ∝ r^α dr on [1,n], HPS 3D density A|x|^{-p} with
  α=2-p. Best at α≈−2, n≈3.50, p≈4: I/D ≈ 0.920655, so
  β_3^{-1} ≈ 1.08618 (2.88% below b(3)=1.11843). Matches Figure 2.
- k-atomic: 1.000, 0.9433, 0.9310, 0.9265, 0.9244, 0.9232 for
  k=1…6, decreasing toward the power law.
- Piecewise-constant log-grid: I/D ≈ 0.921.

Apparent inf of β_3 ≈ 0.921. Apparent inf of β_3^{-1} ≈ 1.086.

## Withdrawn 1.1168

An earlier certificate claimed β_3 ≥ 0.895396, hence
β_3^{-1} ≤ 1.11682 < 1.1185, by lifting a middle-window bound with
the tail polynomial h(D_L, D_R). That lift is false:

- h(0,1) ≈ 0.991, but the HPS power-law trial has I/D ≈ 0.921 when
  placed entirely in that “tail”.
- I_CC ≥ β D_C is false; the correct sub-measure bound is
  I_CC ≥ β D_C M_C.

`certs/beta3_rad.json` is marked withdrawn. Do not cite 1.1168.

## Compact class (correct, not a Theorem 2.2 dent)

On D-measures of aspect ≤ R, after scaling inf(supp z)=1 so
supp z ⊆ [1,R], the mid-radius Rayleigh with F_ij = min f on each
bin-pair, minus the reweighting error P_max(1−fmin) with
P_max = (q−1)/(q+1), q=R^{1/n}, is a valid lower bound.

Face enumeration (`verify_beta3.c`) at R=4, n=18, φ_target=0.906,
0 singular faces, gives

    Q ≥ 0.901924    on aspect ≤ 4,
    1/Q ≤ 1.108741.

That would beat 1.1185 if it held for every radial probability.
It does not: HPS β_3 is an inf over all μ in D_s. Replay:
`certs/beta3_compact.json`. Independent n=16 rebuild:
`verify_beta3.rs`.

A two-window mixture Q ≥ γ_R − p12(γ_R−fmin) with cross terms at
fmin (`lift_global.py`) has grid max p12 ≈ 0.995, so the lift
collapses to fmin. Adjacent-window pairs *are* the t≈t0 pairs.

## Aspect / first variation (search, not a bound)

`aspect_try.py`: geometric t0-chains stay at Q ≥ 0.9379; 200 random
atomic trials stayed above 0.930; the power-law n=3.5 trial is
Q ≈ 0.9207. No explicit measure in that scan dips below the compact
γ. Truncation of those trials to aspect 4 did not increase Q. That
is evidence, not a proof that every measure has aspect ≤ 4, and not
a lift.

The leftover handle is a proof that a minimizer has bounded aspect,
or any other global lower bound strictly above min f.

## s>3

`b(4)≈1.083` would be a real jump if Lemma 4.3 extended. Two-shell
dipoles make I_s(ν) negative for every tested s>3. Closed form at
s=4: Q=−1025/2048. See `work/s_gt_3_notes.md`.

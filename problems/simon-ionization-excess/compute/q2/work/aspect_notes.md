# Aspect lift — residue

Tried to promote the compact γ (aspect ≤ 4) to a global lower bound
on β_3^{rad}. Did not certify.

Replay: `python3 aspect_try.py` writes `certs/aspect_try.json`.

For a probability-constrained critical point the first variation is
V(r)=(Q/2)(r²+D) on the support, with V(r)=∫ g(r,u) m(du) and
g=(r³+u³)/(2 max). A one-point measure satisfies it with Q=1. The
power-law n=3.5 quadrature is only approximately critical
(max relative error about 2×10^{-3} on 64 atoms).

Geometric chains with ratio t0 (the minimizer of f) stay at
Q ≥ 0.9379 through 24 atoms, both for equal m-mass and equal
D-mass. That is above compact γ=0.9019 and above the power-law
0.9207. So the pairs that saturate f=fmin do not, by themselves,
beat the compact number. A search is not a lower bound.

The two-window lift in `lift_global.py` uses fmin on every cross
term and therefore returns essentially fmin once p12 is maximised.

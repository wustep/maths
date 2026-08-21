# Density of the Ulam sequence

- Slug: `ulam-sequence`
- List: P20
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open (growth bound improved; density still unproved)
- Area: Additive combinatorics / OEIS
- Sources: Green 100 #7; OEIS A002858; Steinerberger
- Started: 2026-08-17

## Statement

For the classical Ulam sequence beginning (1,2), it is unknown whether its natural density exists or is positive, and its Fourier concentration lacks a proof-level explanation.

## Tonight

A certified finite advance: a new exact prefix, a covering/automaton certificate, or a documented spectral fact with a verifier. A plot of the first N terms is residue. Fetch Green #7, OEIS A002858, and Steinerberger before searching. Do not claim the density exists unless you prove it.

## Result (2026-08-17)

Density is still open. Following the Clément–Steinerberger majorant with a
longer admissible word and an exact Frobenius maximum,

$$
a_n\le(1443/1000)^n\quad\text{for all }n\ge 1,
$$

and $a_n\le(1442/1000)^n$ for all $n\neq 3$. This beats CS 2025
($a_n\le 1.454^n$ for large $n$). Independently recomputed their
$L=15$ constant as $1.45390220$. Did not beat the Gibbs–McCranie
prefix. Replay: `compute/verify_all.py`.

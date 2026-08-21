# Lonely runner for 14 runners

- Slug: `lonely-runner-fourteen`
- List: P44
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Diophantine approximation / computational combinatorics
- Sources: Sungkawichai and Trakulthongchai, Eleven, twelve, and thirteen lonely runners (arXiv:2604.23906); Trakulthongchai, Nine and Ten Lonely Runners
- Started: 2026-08-17

## Statement

Computer-assisted work in 2025–26 established the lonely-runner conjecture through 13 runners. The next case, 14 runners (13 nonzero relative speeds), remains open.

## Tonight

A certified finite-reduction or modular-sieve certificate for 14 runners, a new excluded speed configuration with an independently checkable witness, or a documented incomplete search. Isolated floating-point scans are not a new bound. Fetch the 13-runner papers before searching.

## Outcome (2026-08-17)

Incomplete: SuperGrok hit quota before a walkthrough. Independently replayed `rk_inclusion.py --selftest` and two p=191 witnesses in `verify_witness.py`. Exhaustive leftover salvage not replayed. LRC(13) open. See `ATTACK.md`.

# Existence of a projective plane of order 12

- Slug: `projective-plane-order-twelve`
- List: P31
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Finite geometry / design theory
- Sources: Moorhouse, Projective Planes of Small Order; 2026 catalogue audit
- Started: 2026-08-17

## Statement

Neither a projective plane of order 12 nor a proof of nonexistence is known. It would be a 2-(157,13,1) design, equivalently a complete set of 11 mutually orthogonal Latin squares of order 12.

## Tonight

A certified new forbidden automorphism type, an explicit construction, or a documented incomplete search. Isolated SAT timeouts are not a new bound. Fetch the current catalogue status before searching.

## Outcome (2026-08-17)

Moorhouse still has no order-12 plane. Published Aut restriction remains $\lvert G\rvert\in\{1,2,3\}$ (Akiyama–Suetake–Tanaka 2023). Order 2 is an involutory elation, equivalent to 11 MOLS with $L[r+6][c]=L[r][c]+6$. Two distinct involution 2-MOLS were constructed and independently verified; each has a drat-trim-verified proof that it admits no third involution-mate. The $t=3$ instance that would forbid the elation timed out (`UNKNOWN`, 45M conflicts / 2396s). Isolated SAT timeouts are not a new bound. Incomplete search, not a bound. See `ATTACK.md`, `WALKTHROUGH.md`, `RESEARCH.md`.

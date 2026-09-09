# Finite handles

The local exact replay reaches 53. OEIS A398173, checked again on
2026-09-09, publishes exact values through 73; the first absent prime is 79.
A replay of the published value at 59 would not improve the record.

| Leaf | Required evidence | State |
| --- | --- | --- |
| Decide whether m(59) is at most 14 (q4) | A valid set, or complete exclusion of sizes 2 through 14 | residue |
| Exact table at 61 through 73 | Witnesses and dual lower replay; compare with the published values | open |
| Extend the exact table at 79 through 199 | Witness and dual lower replay at a prime absent from the record | open |
| Shapes of extremal sets | Affine orbit data with direct arithmetic checks; not a table extension | open |

The completed q3 replay through 53 matches the existing record. It is not a
dent. The inherited 15-set at 59 remains an upper-bound certificate locally;
the published equality has not yet been independently replayed here.
The unrestricted size-at-most-14 question remains open locally. The q4
campaign is wrapped at the user's request, not exhausted mathematically.

Completed: the 15-set upper check in two languages; AP5 UNSAT in Rust and
CaDiCaL; AP6 UNSAT in Rust (also implied by AP5); midpoint partition audits
giving 25 AP4-free classes and 27 AP4-but-AP5-free classes. The audits do not
exclude those classes. Incomplete: unrestricted Rust and SAT prefixes, the
earlier AP5 SAT prefix, AP4's 600-second timeout, and the interrupted C AP5
run. The exact restrictions and artifact names are in `q4/CLAIM.md`.
Search caps and near misses never close a lower-bound leaf. See
`q4/CLAIM.md` for the current assertion. The inherited q4 probes at 79 are
construction diagnostics only; they do not decide its exact value.

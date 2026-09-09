# Finite handles

The local exact replay now reaches 59 and matches OEIS A398173 at that
prime. OEIS continues through 73; the first absent prime is 79.

| Leaf | Required evidence | State |
| --- | --- | --- |
| Exact table at 61 through 73 | Witnesses and dual lower replay; compare with the published values | open |
| Extend the exact table at 79 through 199 | Witness and dual lower replay at a prime absent from the record | open |
| Shapes of extremal sets | Affine orbit data with direct arithmetic checks; not a table extension | open |

Completed: local $m(59)=15$, matching the published term. The 15-set upper
check is in two languages. Size at most 14 is excluded by the AP5 family
(Rust and C in q5, agreeing with the inherited q4 Rust/CaDiCaL runs) together
with 27 AP4-but-not-AP5 named midpoint classes and 25 AP4-free classes, each
UNSAT in C and in Rust. This is a record match, not a dent. The 3-swap
neighborhood of 31 seeds found no 14-set and is not a lower bound on its
own. See `q5/CLAIM.md`.

The q3 replay through 53 also matches the existing record. The inherited
q4 probes at 79 remain construction diagnostics only.

# Two smooth summands for every integer

- Slug: `two-smooth-summands`
- List: P12
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Additive number theory
- Sources: Green 100 #59; Erdős Problem #334
- Started: 2026-08-17

## Statement

For fixed ε>0, it remains unknown whether every n≤N is a sum of two integers whose prime factors are all at most N^ε, for all sufficiently large N.

## Tonight

A certified finite residue cover, an explicit ε with a checkable covering template, or a documented obstruction. Isolated small-N tables are residue unless they imply an infinite covering. Fetch Green #59 and Erdős #334 before searching.

## Outcome (2026-08-17)

Documented residue. No infinite covering and no exponent below Balog
\(4/(9\sqrt e)\). Certified: the trivial \(2\sqrt n+1\) template,
the negative-pseudosquare lemma, \(F(131486759)=83\), \(G(y)\) through
\(y=79\), and exact exception prefixes for \(n^{1/2}\), \(n^{2/5}\),
\(n^{1/3}\) that do not lift. Details in ATTACK.md / RESEARCH.md.

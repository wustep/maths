# Problem attack log

One directory per problem. Do not invent solutions. A log of a failed
attack is more useful than a fake write-up.

## Suggested layout

```
problems/<short-slug>/
  STATEMENT.md     precise statement, sources, what "done" means
  ATTACK.md        chronological log (date, idea, result, next)
  compute/         scripts, notebooks, data
  lean/            formal sketches if any
```

## STATEMENT.md template

```markdown
# <title>

- Status: open | partial | blocked | solved (only if actually solved)
- Area:
- Sources: (papers, OEIS, Erdős problem list, contest statement, …)
- Started:

## Statement

Write the claim in mathematics, not marketing language.
Include definitions.

## Success criteria

What would count as a proof, a counterexample, a bound, or a formalization?

## Related work

Links only. Quote sparingly.
```

## ATTACK.md template

```markdown
# Attack log — <title>

## YYYY-MM-DD

- Hypothesis:
- What we tried:
- Evidence (computation, lemma, obstruction):
- Outcome: dead end | promising | needs formalization
- Next:
```

## Conventions

- Timestamp entries (America/Los_Angeles for Stephen).
- Keep raw computer output in `compute/` rather than pasting megabytes here.
- If Lean is involved, record the toolchain version (`lean --version`).
- Never check in secrets, API keys, or unpublished personal data.

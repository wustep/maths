# Hilbert 16(a) degree 8, q5, 2026-08-29

Grok 4.6 on the existing `problems/hilbert16-degree-8` folder,
starting from `origin/main` `e6fe948` (q4 wrap merged). Stopped on
request before either leftover neighbourhood finished.

## Record

Re-fetched arXiv:2602.06888: still v3, 27 Jul 2026, 2,367 nonempty
degree-8 T-schemes. Bound still ≥ 2,384. Leftover ranks 22–26 and
the depth-3 three-split finished on main.

## Bound

Has not moved. No `q5/certs/new_schemes.json`. No candidate reached
`python3 verify_new.py`. Incomplete search is residue, not a lower
bound. `ATTACK.md` and the README Problems row are unchanged.

## What finished

Nothing in the leftover pair. The q5 stack itself (parent 17,
Rokhlin check, bow-tie probe, skip-prefix check) is what
`sh q5/run_all.sh` replays.

The size-5 count 37,632,123 and the three first-index cuts live
under `compute/q5/certs/`. That file is a count, not a scheme
search.

## What is incomplete

Odd collections of size 5: three first-index shards, stopped by
hand. Combined last progress 18,340,000 evaluations of
37,632,123 tuples. Same twelve published M-schemes as the finished
size-4 sweep. Zero nest hits. No shard printed complete.

| shard | last evals | first-index | schemes | hits |
| --- | --- | --- | --- | --- |
| [0, 11) | 6,140,000 | finished a=0 and a=1; stopped in a=2 | 12 | 0 |
| [11, 32) | 6,120,000 | finished through a=19; stopped in a=20 | 12 | 0 |
| [32, 189) | 6,080,000 | finished through a=44; stopped in a=45 | 8 | 0 |

Pinned even-split BFS remainder (no giant pickle): last printed
line walked 4,754,000, remainder evaluations 3,554,000 of a
4,000,000 cap, queue 4,619,029 and growing. Four published (19,3)
M-schemes, no new scheme. Queue not empty.

Numbers and scheme strings: `leftover_wrap.json` in this folder.

The two open nests remain: ⟨4⊔1⟨2⊔1⟨14⟩⟩⟩ and ⟨14⊔1⟨2⊔1⟨4⟩⟩⟩.

## Scope

The leftover named in the q4 wrap: pinned even-split BFS remainder
and compatible odd collections of size 5. Code in `compute/q5/`.
Replay:

```
cd problems/hilbert16-degree-8/compute
sh q5/run_all.sh
```

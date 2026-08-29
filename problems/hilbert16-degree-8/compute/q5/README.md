# q5 — leftover (19,3) nests

The published census is 2,367 nonempty degree-8 T-curve schemes
(arXiv:2602.06888 v3, §5.3). Seventeen more sit in
`../certs/new_schemes.json`, so the lower bound in this folder is
2,384. q1–q3 finished the radius-1 leftover thicken of every leftover
census triangulation of twist-rank at most 26. q4 finished the
three-split around the twelve published depth-3 M-collections. The
two open (19,3) deep nests remain.

This folder continues the leftover named in the q4 wrap: the pinned
even-split BFS remainder (queue 1,167,098 after 1,200,000
collections) and compatible odd collections of size 5. It does not
re-run leftover thicken or the finished depth-3 three-split.

## Replay

From `problems/hilbert16-degree-8/compute`:

```
sh q5/run_all.sh
```

That re-checks the seventeen and the bow-tie collection.

## Searches

From the same directory, after `python3 prep.py`:

```
python3 q5/even_walk.py bfs q5/even_out/bfs.jsonl 8000000 1200000
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_0-11.jsonl --minsize 5 --shard 0:11
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_11-32.jsonl --minsize 5 --shard 11:32
python3 q5/odd_skel.py 5 q5/even_out/odd_skel5_32-189.jsonl --minsize 5 --shard 32:189
python3 q5/write_certs.py
python3 q5/collect.py
```

The even-split BFS reconstructs the q4 prefix of 1,200,000
collections without re-evaluating schemes, then evaluates the
remainder. It does not write the giant seen/queue pickle (that
stalls the machine). Complete only if the queue empties. There are
37,632,123 compatible odd 5-tuples (`certs/odd_skel5_count.json`).
Size 5 is complete only if every first-index shard finishes and
the shards cover all 189 odd splits. Each shard writes a tiny
`.next` first-index file so a later run can skip finished
indices. Sizes at most 4 are already finished
(`q3/certs/odd_skel4.json`).

A new scheme is a T-curve only after `python3 verify_new.py q5/certs/new_schemes.json`.
An incomplete search is not a lower bound.

## What this run found

See `certs/` after `collect.py`. A new scheme is a T-curve only after
the exact verifier.

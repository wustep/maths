# q1 — Gupta v2 replay and the first unused orders

SuperGrok (2026-08-17) cited Gupta arXiv:2607.23926 as Gold Partition
through 14, not a δ-census. Version 2 (30 Jul 2026) is a full balance
census of every unlabelled 14-element poset. This folder independently
replays the named witnesses and the broken-rung ladder table, then
searches the first orders the census does not cover.

Replay:

```
python3 verify_gupta.py
python3 ladders.py --replay
python3 extend_w10.py
python3 three_rail.py
./run_all.sh
```

Nothing here claims the unrestricted conjecture. A width-3 poset with
δ < 6/17 at n ≤ 14 is incompatible with Gupta's published tail; the
first unused width-3 order is 15.

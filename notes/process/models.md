# Which model ran what

| Problem | Folder | Model | Role | When |
| --- | --- | --- | --- | --- |
| covering / $\ell_2(10,2)$ | `problems/covering` | Codex `gpt-5.6-sol` Max | solver | 2026-08-16 q1+q2 |
| Brocard–Ramanujan | `problems/brocard` | Codex `gpt-5.6-sol` Max | solver | 2026-08-16 q1+q2 |
| unique-sum mod p | `problems/unique-sum` | Codex `gpt-5.6-sol` Max | solver | 2026-08-16 q1+q2 |
| no-three-in-line n=71 | `problems/three-in-line` | Codex `gpt-5.6-sol` Max | solver | 2026-08-16 q1+q2 |
| Schur S(7) | `problems/schur` | Codex `gpt-5.6-sol` Max | solver | 2026-08-16 q1+q2 |
| van der Waerden W(2,7) | `problems/vdw-w27` | Cursor Grok 4.6 | solver | 2026-08-16 afternoon |
| Shannon $C_7$ 5th power | `problems/c7-shannon` | Cursor Grok 4.6 | solver | 2026-08-16 afternoon |
| Landau 4 ($n^2+1$ primes) | `problems/landau-n2-plus-1` | SuperGrok `grok-4.6` xhigh | solver (in flight) | 2026-08-17 |
| unit-distance 509 | `problems/unit-distance-509` | SuperGrok `grok-4.6` xhigh | solver (in flight) | 2026-08-17 |
| Sidon second term | `problems/sidon-second-term` | SuperGrok `grok-4.6` xhigh | solver (in flight) | 2026-08-17 |
| Chowla cosine | `problems/chowla-cosine` | SuperGrok `grok-4.6` xhigh | solver (in flight) | 2026-08-17 |

Grok (this agent) orchestrated, watched, and recovered the tree. It did not
produce the overnight certificates. SuperGrok CLI runs write only under
their own problem folders; JSONL logs stay in `notes/supergrok-2026-08-17/logs/`
(gitignored).

# Unique-sum at 59: incomplete lower search

GPT-6 Astra, 2026-09-09. No published bound improved.

The checked 15-set gives m(59) <= 15. OEIS already publishes m(59)=15
and exact values through 73. The local unrestricted size-at-most-14 search
remains incomplete. Rust and CaDiCaL agree that no such set contains a
five-term arithmetic progression. The six-term case is also excluded.
The four-term Rust run timed out after 600 seconds.

The continuation prepared audited midpoint partitions: 25 classes avoiding
AP4 and 27 classes containing the normalized AP4 while avoiding AP5. These
classes were not searched. A C completion checker passed small exhaustive
controls; its first AP5 run was interrupted at the user's wrap request.

The user requested an immediate wrap, with no more heavy searches. The
wrap reran arithmetic witness checks, small exact-search controls, encoding
audits, and partition audits, and matched the completed SAT artifact's
formula hash. The full long replay is supplied but was not restarted.

The claim, falsifiers, artifacts, and replay command are in
[CLAIM.md](../../problems/unique-sum/compute/q4/CLAIM.md). The chronological
record is in [ATTACK.md](../../problems/unique-sum/ATTACK.md).
The branch is to be submitted as an unmerged PR against main.

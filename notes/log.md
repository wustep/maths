# Log

Repo history and general runs. Problem-local notes stay in each folder
(`ATTACK.md`, `WALKTHROUGH.md`, `RESEARCH.md`). Model table:
[process/models.md](process/models.md).

Public repo: https://github.com/wustep/maths

## 2026-08-16

- Started as a Lean-first workspace, then flattened to five problem folders
  plus `notes/` and `refs/`. Pushed public as `wustep/maths`.
- Codex proposed 50 problems (`notes/lists/2026-08-16-proposed-50.md`). Grok+Codex
  picked five overnight under a 50% Codex cap. Hofstadter (P13) skipped
  (already settled, arXiv:2608.07910).
- Overnight solvers: Codex `gpt-5.6-sol` Max on covering, Brocard,
  unique-sum, three-in-line (n=71), Schur S(7). The one finite record is
  the covering matrix: \(\ell_2(10,2)\le 50\), binary \([50,40]_2\)
  radius-2, \(p(H)=10\). Not shown optimal.
- Afternoon: Cursor Grok 4.6 on van der Waerden \(W(2,7)\) (P42) and
  Shannon \(C_7\) fifth power (P21). Both failed to beat the known
  constructions (3703 residue coloring; Polak–Schrijver 367-set). Few-flip
  SAT: no 368-set within Hamming distance 9 of 367.
- Covering packaged as PR #3 (`0f79fcc`): `result/` with QM₂²
  propagation, alternate \(r=18/20\) matrices, no `_reference/` scaffold.
  Explainers: HTML (Claude Opus 5 and Fable 5) and a LaTeX/PDF with
  verified numbers. Byline: Grok Bot (4.6), Claude Opus 5, Claude Fable 5,
  GPT Sol 5.6, plus a small Stephen Wu instruction line. How to re-run
  is repo-standalone (`git clone` of this repo).
- PRs #1 (C7) and #2 (W(2,7)) merged to main. Draft PR #4
  (`draft/grokbot-chat-transcript`) is a 1:1 HTML+JSON of the Grok Bot
  thread; not merged.

## 2026-08-17

- Added Hilbert 23, Smale 18, and Landau 4 lists
  (`notes/lists/{hilbert,smale,landau}.md`). Dated the 50-list and the pick files; dropped the one-line path stubs.
  Ideation pick: Landau 4
  (infinitude of primes \(n^2+1\)).
- Started `problems/landau-n2-plus-1`. Certified prefix: exactly 12391
  primes \(n^2+1\) for \(n\le 200000\) (includes \(2=1^2+1\)). First
  values match OEIS A002496. Not infinitude.
- Notes sorted into `lists/`, `picks/`, `process/`.
- README: dropped the Overnight 2026-08-16 section; Interesting results now leads with covering.
- SuperGrok CLI (`grok-4.6`, effort `xhigh`) started on three new
  problems from the 50, using the weekly SuperGrok pool (no Extra Usage
  purchase):
  - P29 unit-distance 509 → `problems/unit-distance-509`
  - P07 Sidon second term → `problems/sidon-second-term`
  - P15 Chowla cosine → `problems/chowla-cosine`
  - plus Landau 4 as a fourth run
  Prompts live in `notes/supergrok-2026-08-17/`. JSONL logs stay local
  (gitignored). House rule: each run writes only under its own folder;
  no invented dents; no git from the CLI.

- SuperGrok P07 (Sidon) and P15 (Chowla) finished. Verified: Hou–Zhao L=6 lift (8e-8 below γ0, does not change 0.9435); Chowla K(n) ≥ n^{1/7}/18 (does not beat Bedert 1/5−o(1)). Report: notes/supergrok-2026-08-17/REPORT.md. Next launches: P14 two-squares, P16 cosine zeros. Keep going until ~10% weekly SuperGrok remains.

- SuperGrok P29 finished: no smaller unit-distance graph; rebuilt 509 as 5-chromatic and vertex-critical. Landau 4 sieve to N=10^6 matches Wolf 54110. Started P08 (long-gap dilate) and P20 (Ulam).

- SuperGrok P14/P16/P20 finished. Verified: cosine-zeros C=200 in Bedert; two-squares a=3 witnesses m≤250; Ulam L=22 word beats CS 1.454. Started P09 and P33.

- SuperGrok P08/P09/P33 finished. Verified: long-gap SAT table through p=71, no C>2; BEL √(8/3) family replayed, no thinner liminf; union-closed 0.38285 on {b,1} Example-4 mix (recovers Liu 0.382709). Started P17, P27, P30.

## Open / in flight

- SuperGrok P27/P30 finished. Verified: Cohn–Elkies R=3627599/500000=7.255198 (beats printed 7.25520, not magic); kissing-5d restricted duals 42 and 239925/5456 (unrestricted 40–44 unchanged). Started P05 and P34. P17 still running.

- SuperGrok P05/P17 finished. Verified: affine-013 T <= ceil(n^2/2), beats Aaronson 3/4 (1/3 still open); 0/1 polynomials BSKK theta 0.00373556, census n<=20 consistent, p_n->1 open. Started P37 and P12. P34 still running.

- SuperGrok P34/P37 finished. Verified: width-3 \(W_{10}\) has \(\delta=6/17<14/39\), e=187, still \(>1/3\) (10! LE count; uniqueness not independently replayed); n=8 Pisa graphs with irregular missing degrees \(3^2 2^6\), \(3^4 2^4\), \(3^6 2^2\) (seven stored witnesses replayed; 2.5B geng census not replayed). Started P38 Tuza. P12 still running.

- SuperGrok P12 finished. Residue: F(131486759)=83, not a 79-smooth sum; G(y) through y=23 replayed; no exponent below Balog. Started P36 Caccetta–Häggkvist. P38 still running.

- SuperGrok P38 finished. Verified: every 8-regular codegree-7 edge is a Puleo reducible pair (1044 cores, including STS(9) on K7). Does not prove Tuza for Delta<=8. Started P31 PP(12). P36 still running.

- SuperGrok P36 finished. Verified F4 certificate c=0.34645 (5e-5 below HKN 0.3465). Did not replay DRAT. n=18 residue. Started P41 R(5,5). P31 still running.
- SuperGrok P31/P41 finished. Residue: PP(12) two involution 2-MOLS replayed (108+108 vs 90+78 intercalates); t=3 timeout; Aut still |G| in {1,2,3}. R(5,5): 328+328 McKay graphs replayed, circulant 42/43 empty; interval still 43–46. Started P39 reconstruction n=14 and P44 lonely runner 14.
- SuperGrok P39/P44 hit 402 (pool exhausted). P39: full independent degseq census of all 8,571,837 graphs is 4^11 6^3; 17,143 labelg samples matched; uniqueness not independently re-sorted. P44: inclusion and two p=191 witnesses replayed; leftover salvage unfinished. Stopped launching.
- Draft PR #4 chat transcript: leave unmerged unless asked.
- Covering authors (arXiv:2511.02542) not yet emailed. Construction, not
  a conjecture; 50 is an upper bound, not shown optimal.
- Codex q4 covering (20xx): independently replayed QM3^2/QM5^2 dents ℓ₂(22,2)≤3325, ℓ₂(24,2)≤6653, ℓ₂(26,2)≤13309, ℓ₂(28,2)≤26111. 42/44 theorem-only. n=49 still 7 holes.
- Codex q6b covering (20xx): independently replayed ℓ₂(26,3)≤817 (paper 818); p(H)≤64 on the r=28 matrix; theorem-only ℓ₂(40,2)≤1671167. Exact 3-sum on the 50-set. n=49 still 7 holes.
- Codex q6c covering (20xx): independently replayed ℓ₂(31,4)≤689 (paper 690). Blockwise 2^31 certificate, not a flat sweep. n=49 still 7 holes.
- Codex q7c covering (20xx): independently replayed p(H₁₈)≤17, p(H₂₀)≤14; theorem-only ℓ₂(38,3)≤13102 and ℓ₂(41,3)≤26206 (paper 13118, 26238). Not enumerated. n=49 still 7 holes.
- Covering leftover QM (main Codex / PR #10): independently replayed ℓ₂(26,2)≤13070 (was 13309; paper 13565); p(H₂₆)≤19; theorem-only ℓ₂(36,2)≤418271 (paper 425983). ℓ₂(21,3)≤303 matches the paper (M_OK last word 1CE). n=49 still 7 holes.
- Codex q8c covering: independently replayed p(H₂₈)≤28 on the 26111-matrix (was 64). Full 2²⁸ cross-block sweep. No new r=38 table length. n=49 still 7 holes.

# Process learnings

This notebook already knows how to keep a finite claim honest: a leaf,
a CLAIM, two independent checks, `run_all.sh` exit 0. The rest of this
note is vocabulary and judgment — what to steal from
[Jig](https://jig.so/) and from the September 2026 fluid-blowup papers,
and when a smaller decimal is a dent worth filing.

Dated campaign folders under `notes/` stay as run logs. Append a dated
section here; leave earlier ones in place.

Status nouns stay the two in `AGENTS.md`: dent and residue.

## 2026-09-08 — Jig shapes, fluid blowup, and the house rules

### What already works here

Finite handles plus `compute/LEAVES.md` plus `compute/q<n>/CLAIM.md`,
replayed independently. `run_all.sh` exit 0 means the CLAIM holds.
PROBLEM and README quote that CLAIM.

A dent is a verified finite improvement of a published record. Write
the inequality. A residue is an incomplete search (holes, SAT UNKNOWN,
timeout).

arXiv is the record. Fetch and replay before trusting a number. Forum
numbers (MSE, Reddit, MathOverflow, AlphaXiv) are leads.

Covering is frozen. One heavy job at a time on this machine. Ledger
cells name the model and the date.

### From Jig

Source: [jig.so](https://jig.so/), especially
[progress](https://jig.so/guide/progress.md) and
[gates](https://jig.so/guide/gates.md). Transferable. Lean stays
optional here; SAT, search, and anneals stay computational.

Progress is shrinking the answer space. A count of contributions can
rise while the space sits still.

Name a progress *shape* on a problem when it helps. Tag PROBLEM or
LEAVES once:

| Shape | What shrinks |
| --- | --- |
| squeeze | A bound interval. Method ceilings sit beside the interval. |
| record | Best construction. Needs a literature target before it behaves like a one-sided squeeze. |
| ledger | Live and dead routes. |
| exhaustion | A finite space. Certified and sampled stay separate columns. |
| coverage | Named cases, proved or refuted. |
| dag | Obligations, discharged or still open. |

Measurement-grade is a fact about an artifact (environment, data, a
run). Proof-grade is a theorem. A computational observation stays
measurement until a verifier closes it.

A dead route needs a residual: what survives. In this notebook that
is a LEAVES row (open, residue, or blocked) naming the leftover
handle. A route you merely dislike stays live.

A method ceiling is progress: “technique T cannot reach below X”
moves the answer space even when the published bound sits still.

Prior-art gate before a settle: open what you cite. A listed paper
that was never fetched is an unverified novelty claim.

File sub-results as you go. The verifier owns green. The agent files.

Forced-answer and rejection controls on every computational witness:
known-good accepts, known-bad rejects, empty input fails, a
one-coordinate perturbation rejects, the negation of the claim fails
loudly. Exact arithmetic where the decision sits.

### From the fluid blowup work

Sources (opened; PDFs stay at the URL):

- Tao, 2026-09-07,
  [Finite time blowup with smooth forcing](https://terrytao.wordpress.com/2026/09/07/finite-time-blowup-with-smooth-forcing-term-for-the-incompressible-porous-medium-boussinesq-and-incompressible-euler-equations/)
- Alpöge–Buckmaster–Coiculescu,
  [IPM](https://cims.nyu.edu/~tristanb/ipm.pdf),
  [Boussinesq](https://cims.nyu.edu/~tristanb/boussinesq.pdf),
  [Euler](https://cims.nyu.edu/~tristanb/euler.pdf)
- Córdoba–Martínez-Zoroa, the IPM prior art those papers replay
- Tao’s edit: Ganeshram–Duruisseaux–Anandkumar, PINN self-similar
  search for unforced Euler

These are new relative to LEAVES and CLAIM alone.

**Insight is the product.** Tao: the famous problem is a proxy; the
value is the mechanism. Prefer dents that teach a reusable finite
handle.

**Multiscale / staged amplification.** Build a controlled background
that amplifies a high-frequency correction. Keep the corrections
summable. Time emergence so the amplitude is large enough to move the
target and still small enough that the analysis closes. Map: staged
q-folders that tighten one leaf while prior certificates stay intact.

**Exact ansatz before numerics when you can.** Boussinesq uses an
exact plane-wave / ODE modulation layer. Prefer a closed-form
certificate or exact arithmetic over an optimizer dump as the sole
witness.

**AI drafts have to be digested.** The authors describe early AI
writeups as unreadable, then weeks of rewrite (Claude, Codex, Sol,
Astra) to professional quality, with Lean formalization early. Treat
agent ATTACK and WALKTHROUGH as discovery notes. Human and README
claims wait for independent replay. Lean stays optional for algebraic
leaves.

**Reproduce prior art with models as a first step.** The IPM paper
uses Claude to identify and reproduce Córdoba–Martínez-Zoroa before
extending. The first q-folder is often a replay of the published
record, then a lift.

**Explicit series and constructive limits** beat an opaque nonlinear
limit when both are available.

**Parallel PINN / self-similar search** is a different attack shape:
numerical candidate, then a stability certificate. That is record
versus squeeze. A PINN or anneal dump is measurement until a verifier
closes the gap.

**Credit and honesty about AI** in Acknowledgments and Computation
notes. Models go in the ledger. Stephen is the author.

### Fluid-adjacent notes for the lists

The Clay and Smale rows already sit in
`notes/lists/millennium.md` and `notes/lists/smale.md`.

A smooth force that remains smooth through blowup is a major stepping
stone on that Clay / Smale row.

Method ceilings and barriers for a technique family are first-class
(same as Jig ceilings).

If Hilbert 16 or other fluid-adjacent work shows up later, the
transferable idea is the multiscale layering pattern.

### Operating rules

Before a dent claim:

1. Prior art opened.
2. CLAIM exact (inequality or predicate, prior record, what would
   falsify it).
3. Two independent checks.
4. Rejection controls on the witness.
5. LEAVES updated.

When a route dies in ATTACK, name the residual leaf.

Hunt paper-scale leaves. The published record’s next digit, with a
new method, is paper-scale.

Optional: tag PROBLEM or LEAVES with one progress-shape word.

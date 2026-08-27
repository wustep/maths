# Literature notes — simon-ionization-excess q2

Session 2026-08-27 (continued). Re-opened the HPS abs this pass to
confirm v1 is still the only version before comparing a leading-
coefficient claim against 1.1185. URLs actually opened this session.
One line each: what the source STATES, then what it does NOT state.

- https://arxiv.org/abs/2504.18487 — re-opened 2026-08-27. STATES
  still only v1 (25 Apr 2025); abstract line
  \(N_c(Z)<1.1185Z+O(Z^{1/3})\). Does NOT list a v2.

## Verdict (read from the papers, not abstracts)

No paper opened after Hundertmark–Pattakos–Schulz arXiv:2504.18487v1
(25 Apr 2025; still the only arXiv version) claims a fermionic leading
coefficient below 1.1185. No paper proves \(N_c\le Z+C\) or
\(N_0(Z)-Z\) bounded for the many-body Schrödinger operator. No paper
claims a unique \(N_0(Z)\) for any \(Z>1\). No later paper gives a
sharper explicit remainder class than HPS printed \(2.96\), \(3.90\),
and \(4\).

HPS v1 remains the published non-asymptotic record on the leading
coefficient: \(N_c<1.1185Z+4Z^{1/3}\) for \(Z\ge 4\), with
\(1.1184<b(3)<1.1185\).

The only later arXiv paper on excess charge of atoms is
Benguria–González-Brantes 2511.07582v1 (10 Nov 2025). It is
statistics-independent / bosonic, leading coefficient \(1.4811\),
and does not beat 1.1185 for fermions. It is the replacement for
2207.08328v2, whose abs comment says that version has errors.

---

## Direct answers

- Leading coefficient below 1.1185? **No paper claims this.**
- \(N_c\le Z+C\) or \(N_0(Z)-Z\) bounded (Schrödinger)? **No paper
  proves this.** Lewin CR Physique (online 7 May 2025; manuscript
  accepted 31 Mar 2025, before HPS) still says even \(C=10^{100}\)
  is unknown.
- Unique \(N_0(Z)\) for \(Z>1\)? **No paper claims this.** Lieb 1984
  gives uniqueness only for hydrogen: \(N_c=2\).
- Better explicit remainder class after HPS v1? **No published
  paper.** 2511.07582 has remainder \(3.1516Z^{1/3}\) on a
  \(1.4811Z\) leading term (bosonic). Schulz thesis (30 Jul 2025)
  restates the HPS leading 1.1185 (and writes \(o(Z^{1/3})\),
  weaker than the paper’s explicit \(O(Z^{1/3})\)).

---

## HPS 2504.18487 — only v1 exists

- https://arxiv.org/abs/2504.18487 — Abs of **v1 only** (submitted
  and updated 2025-04-25; comment “50 pages, 2 figures”). STATES
  \(N_c(Z)<1.1185Z+O(Z^{1/3})\) with an explicit lower-order term;
  improves Lieb 1984 and Nam 2012. Does NOT list a v2, a journal
  reference, or \(N_c\le Z+C\).
- https://arxiv.org/html/2504.18487v1 — Full HTML of v1. STATES
  Theorem 2.2: \(N_c<b(s)Z+c(s)Z^{1/3}\) for \(s\in(1,3]\),
  \(b(s)=\max_{t\in[0,1]}(1+t^{s-1})/(1+t^s)\). Prop. 2.4
  (\(Z\ge 2\)): \(N_c<\frac12(\sqrt2+1)Z+2.96Z^{1/3}\). Prop. 2.5
  (\(Z\ge 4\)):
  \(N<b(3)Z+3.90Z^{1/3}+0.0134+0.184Z^{-1/3}+0.0196Z^{-2/3}\) with
  \(1.1184<b(3)=\frac23\frac{(1+\sqrt2)^{1/3}}{(1+\sqrt2)^{2/3}-1}<1.1185\).
  Simplified \(N_c<1.1185Z+4Z^{1/3}\) for \(Z\ge 4\). Also writes
  \(N<1.12Z+4Z^{1/3}\) as a coarser form. LT factor 1.456 of
  Frank–Hundertmark–Jex–Nam enters \(\kappa\) in the remainder
  (Section 6), not \(b(s)\). Does NOT prove bounded excess; does
  NOT claim unique \(N_0(Z)\) for \(Z>1\); does NOT claim a
  coefficient below 1.1185.
- https://doi.org/10.48550/arxiv.2504.18487 — Same v1 preprint
  landing. STATES cited-by 0 on that page. Does NOT list a later
  version.
- https://arxiv.org/pdf/2504.18487 — Same v1 PDF text as the HTML.
  STATES the same theorems. Does NOT add a v2.
- https://export.arxiv.org/api/query?id_list=2504.18487 — API
  returns only 2504.18487v1, updated 2025-04-25. Does NOT return
  v2 or a journal id.

Replay of printed constants (already in `compute/q1/certs/hps_replay.json`):
\(b(3)\approx 1.1184338\in(1.1184,1.1185)\),
\(b(2)=(\sqrt2+1)/2\approx 1.20710678\). Nam’s \(1.22\) is
\(\beta^{-1}\) with \(\beta\ge 0.8218\), so \(1/\beta\le 1.2169<1.22\).

---

## Nam 1009.2367v3 — replayed

- https://arxiv.org/abs/1009.2367 — Latest is **v3** (26 Nov 2011),
  “to appear in Commun. Math. Phys.” STATES
  \(N_c<1.22Z+3Z^{1/3}\), beats Lieb for \(Z\ge 6\);
  \(\limsup N_c/Z\le 1.22\) in magnetic / pseudo-relativistic
  extensions. Does NOT claim \(N_c\le Z+C\).
- https://arxiv.org/abs/1009.2367v3 — Version page. STATES v1
  13 Sep 2010, v2 22 Sep 2010, v3 26 Nov 2011. Does NOT change
  the 1.22 coefficient across the abs text of v3.
- https://arxiv.org/html/1009.2367v3 — Full HTML. STATES Theorem 1:
  if \(E(N,Z)\) is an eigenvalue then either \(N=1\) or
  \(N<1.22Z+3Z^{1/3}\); “1.22 can be replaced by \(\beta^{-1}\)”.
  Lemma 1 + Proposition 1: \(\beta\in[0.8218,0.8705)\),
  \(\alpha_N\to\beta\),
  \(\alpha_N\ge\frac{N}{N-1}[\beta-3(\beta/6)^{1/3}N^{-2/3}]\).
  Printed \(g(\lambda)\) max \(0.8218066\ldots\) at
  \(\lambda\approx 0.843476\); trial
  \(\beta_{\mathrm{rad}}\le 115/81-\frac12\ln 3=0.8704\ldots\).
  Ionization conjecture \(N_c\le Z+1\) or \(Z+2\) stated as open.
  Does NOT prove bounded excess; does NOT unique-\(N_0(Z)\) for
  \(Z>1\); does NOT beat 1.1185 (this is 2011).
- https://arxiv.org/pdf/1009.2367 — Same v3 PDF text. STATES the
  same Theorem 1. Does NOT add later constants.

Replay (`compute/q1/certs/nam_beta.json`): \(\beta>0.8218\) and
\(\beta<0.8705\) hold; \(1/0.8218\approx 1.21684\), which Nam
rounds to 1.22.

---

## Nam surveys 1209.3642v2 and 2206.15393v1

- https://arxiv.org/abs/1209.3642 — Abs of **v2** (7 Dec 2012).
  STATES a review of the ionization conjecture. Does NOT claim a
  new coefficient.
- https://arxiv.org/html/1209.3642v2 — Full HTML. STATES
  conjecture \(N_c\le Z+1\) or \(Z+2\); Lieb \(N_c<2Z+1\) settles
  hydrogen; FS/SSS \(N_c\le Z+CZ^{5/7}\) best for large \(Z\);
  Theorem 2 restates Nam \(N<1.22Z+3Z^{1/3}\); bosons
  \(N_c/Z\to t_c\approx 1.21\); Nam’s fermionic remainder uses LT
  (Pauli). Open: convexity, “binding of \(N\) implies \(N-1\)”,
  bounded radii, bounded ionization energy. Does NOT prove
  \(N_c\le Z+C\); does NOT unique \(N_0(Z)\) for \(Z>1\).
- https://ar5iv.labs.arxiv.org/html/1209.3642 — Same survey text
  as the official HTML. Does NOT add numbers.
- https://arxiv.org/abs/2206.15393 — Abs of **v1** (30 Jun 2022),
  Lieb 90th-birthday chapter. STATES a review. Does NOT claim a
  new bound.
- https://arxiv.org/html/2206.15393v1 — Full HTML. STATES Zhislin
  binding for \(N<Z+1\); Theorem 4 Lieb \(N_c<2Z+1\) for all
  \(Z>0\), settles hydrogen; full short proof of Lieb (multiply by
  \(|x_N|\), drop kinetic by \(|x|(-\Delta)+(-\Delta)|x|\ge 0\),
  triangle \(|x|+|y|\ge|x-y|\)). Theorem 5 restates Nam 1.22.
  Lenzmann–Lewin: no eigenvalue if \(N\ge 4Z+1\). LSST
  \(N_c/Z\to 1\); FS/SSS \(Z+O(Z^{5/7})\). Bosons: \(t_c\approx 1.21\),
  Benguria–Tubino Hartree \(t_c<1.5211\). Conjecture 2
  (\(N_c\le Z+C\)) still open. Does NOT mention HPS (2022);
  does NOT unique \(N_0(Z)\) for \(Z>1\).

Lieb 1984 replayed here from Nam’s write-up of the published
argument (APS HTML was Cloudflare-blocked; see below).

---

## Lieb, Phys. Rev. A 29 (1984) 3018–3028

- https://inspirehep.net/literature/14268 — INSPIRE record
  Lieb:1983ru. STATES abstract: \(N_c<2z+1\); molecule of \(K\)
  atoms \(N_c<2Z+K\); hydrogen \(N_c=2\), so \(H^{--}\) not
  stable; statistics plays no role; static nuclei; also
  magnetic / relativistic kinetic energy. Does NOT give the
  body of the proof; does NOT claim unique \(N_0(Z)\) for
  \(Z>1\); does NOT claim a coefficient below 2.
- https://inspirehep.net/api/literature/14268?format=json —
  Same metadata. STATES DOI 10.1103/PhysRevA.29.3018, pages
  3018–3028, also reprinted in *The Stability of Matter*
  pp. 91–101. Does NOT attach a PDF.
- https://journals.aps.org/pra/abstract/10.1103/PhysRevA.29.3018
  — Cloudflare bot-check this session. STATES nothing readable
  beyond the challenge page. Full APS HTML/PDF **not obtained**.
- https://web.math.princeton.edu/~lieb/publications.html —
  STATES the bibliographic line “Bound on the Maximum Negative
  Ionization of Atoms and Molecules, Phys. Rev. 29A, 3018–3028
  (1984)” and the short PRL 52, 315–317 (1984). Does NOT host
  the PDF at that URL.

Replay of the atomic bound is the argument written out in
2206.15393v1 §2 (and 1209.3642v2, HPS §3): \(N<2Z+1\) strict
because the triangle inequality is strict a.e. Combined with
Zhislin \(N_c\ge Z\) (actually binding for \(N<Z+1\)), this
forces \(N_c=2\) at \(Z=1\). For \(Z=2\), Lieb only gives
\(N_c\le 4\), not a unique \(N_0(2)\).

---

## Benguria–González-Brantes–Tubino 2207.08328 — v2 flagged; PDF gone

- https://arxiv.org/abs/2207.08328 — Latest is **v2** (updated
  3 Nov 2025). Abs comment: **“This version is not definite and
  has errors.”** Abs still STATES the 2022 claim: statistics-
  independent bounds, “best for bosons for all \(Z\)” and “best
  for fermions with \(Z\le 26\)”. Does NOT withdraw the abs
  numbers; the comment is the warning.
- https://arxiv.org/abs/2207.08328v1 — v1 (18 Jul 2022). STATES
  the same abs as v2, **without** the errors comment.
- https://arxiv.org/abs/2207.08328v2 — v2 landing. STATES the
  errors comment. Official HTML 404; official PDF 404.
- https://export.arxiv.org/api/query?id_list=2207.08328 — API
  confirms v2 updated 2025-11-03T19:40:21Z, comment as above.
- https://export.arxiv.org/pdf/2207.08328v2 — **HTTP 404.**
  v2 body is not on arXiv.
- https://export.arxiv.org/pdf/2207.08328v1 — **HTTP 200**, 17
  pages. STATES v1 title/abs (“best … \(Z\le 26\) … iron”).
  Stream extract of this session did not recover the theorem
  line; numbers below are from ar5iv HTML of v1/v2.
- https://ar5iv.labs.arxiv.org/html/2207.08328 — HTML of the
  claimed theorem. STATES Theorem 2.1 (bosonic atoms):
  \(N<1.5211Z+1+aZ^{1/3}\) with \(a=0.29363\) for \(Z\ge 6\);
  small-\(Z\) lines \(Z=1\): \(N<2.9489<3\); \(Z=2\):
  \(N<4.4824<5\); \(Z=3\): \(N<6.0286<7\); \(Z=4\):
  \(N<7.5741<9\); \(Z=5\): \(N<9.1180<11\). Remarks claim this
  beats Lieb for all statistics and beats Nam for fermions
  \(1\le Z\le 26\). Does NOT prove \(N_c\le Z+C\); does NOT
  unique \(N_0(Z)\) for \(Z>1\) (the \(Z=2\) line is \(N<5\),
  same integer ceiling as Lieb). **Not a record:** authors
  later marked v2 as having errors.
- https://ar5iv.labs.arxiv.org/html/2207.08328v1 and
  https://ar5iv.labs.arxiv.org/html/2207.08328v2 — Texts
  compared this session: **identical**. So ar5iv v2 is not a
  corrected theorem; it is the same body as v1 (v2 PDF missing).

**What survives numerically from 2207.08328v2?** Nothing that
can be cited as a published record. The abs comment plus the
missing v2 PDF plus the 2511.07582 acknowledgment (Hundertmark
and Schulz “pointing out errors in a previous version”) mean
the 1.5211 / 0.29363 / small-\(Z\) / “best for \(Z\le 26\)”
claims are withdrawn. They also never beat 1.1185 as a leading
fermionic coefficient.

---

## Replacement: Benguria–González-Brantes 2511.07582v1 (after HPS)

- https://arxiv.org/abs/2511.07582 — **v1 only**, 10 Nov 2025.
  STATES an upper bound independent of statistics, improves
  Lieb for \(Z\ge 12\). Does NOT mention 1.1185; does NOT claim
  to beat Nam or HPS for fermions at large \(Z\).
- https://arxiv.org/html/2511.07582v1 — Full HTML. STATES
  Theorem 1.1 (title says bosonic atoms; proof uses symmetry of
  \(|\psi|^2\), so the argument is written as statistics-
  independent): \(N<1.4811Z+3.1516Z^{1/3}\) for \(Z\ge 12\).
  Uses Nam’s \(\beta\in[0.8218,0.8705)\), Coulomb uncertainty,
  Lieb–Oxford \(\le 1.5765\), a numerical GNS constant 0.2812,
  and \(C_{\mathrm{IE}}\approx 0.1242\). Acknowledgments:
  Hundertmark and Schulz “pointing out errors in a previous
  version of this manuscript” (the 2207 line). Does NOT claim
  a leading coefficient below 1.1185 (1.4811 is worse than
  Nam’s 1.22 and HPS’s 1.1185 for fermions); does NOT prove
  \(N_c\le Z+C\); does NOT unique \(N_0(Z)\) for \(Z>1\); does
  NOT give a remainder class better than HPS’s printed
  \(O(Z^{1/3})\) on the 1.1185 term.

---

## Corso–Ried 2403.04347v2 — LT variational, not ionization

- https://arxiv.org/abs/2403.04347 — Latest **v2** (21 Dec 2024),
  comment “Corrected a few typos.” STATES a variational problem
  for CLR/LT constants. Does NOT mention atoms, \(N_c\), or
  excess charge.
- https://arxiv.org/abs/2403.04347v2 — Same. Does NOT change
  an ionization coefficient.
- https://arxiv.org/html/2403.04347v2 — Full HTML. STATES
  \(L_{1,1,1}/L_{1,1,1}^{\mathrm{cl}}\le 1.44655\), a marginal
  improvement on Frank–Hundertmark–Jex–Nam 1.45579; induction
  in dimension extends \(\sigma=1\) to all \(d\ge 1\). Does NOT
  mention ionization, \(N_c\), or \(b(s)\). HPS’s leading
  \(b(3)\) is a classical max of \((1+t^{2})/(1+t^{3})\); the
  1.456 LT factor sits only in HPS \(\kappa\) (remainder).
  Even if one swapped 1.456 for 1.44655, that would not move
  the printed leading 1.1185. This paper is also **before**
  HPS (Dec 2024 vs Apr 2025).

---

## Lewin, CR Physique 26 (2025) 369–380

- https://comptes-rendus.academie-sciences.fr/physique/item/10.5802/crphys.249.pdf
  — Full PDF opened. STATES Open Problem 1: prove
  \(N_{\max}\le Z+CM\) for a universal \(C\) (ideally 1 or 2);
  “no proof of (5) has been provided yet, even with a crazy
  constant like \(C=10^{100}\)”. Then-best explicit: Lieb
  \(N_{\max}<2Z+M\); for atoms Nam \(N_{\max}<1.22Z+3Z^{1/3}\);
  for \(Z\le 118\) this is “\(N_{\max}\le Z+40\)”; LSST
  \(Z+o(Z)\); FS/SSS \(Z+O(Z^{5/7})\); Solovej HF with huge
  \(C\). Manuscript received 6 Nov 2024, revised 28 Mar 2025,
  accepted 31 Mar 2025, online 7 May 2025. Does NOT cite HPS
  (HPS is 25 Apr 2025, after acceptance). Does NOT prove
  bounded excess; does NOT unique \(N_0(Z)\) for \(Z>1\).

---

## Other 2025–2026 papers opened (not a fermionic-leading improvement)

- https://arxiv.org/abs/2502.15444 and
  https://arxiv.org/html/2502.15444v1 — Benguria–Siedentop,
  21 Feb 2025 (before HPS). STATES excess-charge bounds for
  **generalized TFW density functionals**, not the many-body
  Schrödinger operator. For \(3/2<p<2\), \(Q\) uniformly
  bounded in \(Z\); Hartree-type \(N\le 1.5211Z\). Does NOT
  change the Schrödinger leading coefficient; does NOT apply
  to Simon 2000 #9 as a new bound.
- https://doi.org/10.5445/ir/1000183607 — Schulz KIT thesis
  landing (published 30 Jul 2025; defense 29 Apr 2025). STATES
  in the abstract \(N_c(Z)<1.1185Z+o(Z^{1/3})\) and Hartree
  \(t_c<1.47\). This is the HPS result (same leading 1.1185;
  the \(o(Z^{1/3})\) is weaker notation than the paper’s
  explicit \(O(Z^{1/3})\)). Does NOT claim a coefficient below
  1.1185; does NOT prove \(N_c\le Z+C\).

---

## Citation / “anything later than HPS v1?” searches

Opened, not just searched:

- https://api.semanticscholar.org/graph/v1/paper/ARXIV:2504.18487?fields=title,year,citationCount,citations.externalIds,citations.title,citations.year,citations.authors
  — STATES `citationCount: 0`, `citations: []`. Does NOT list a
  later improvement.
- https://api.openalex.org/works?filter=doi:10.48550/arXiv.2504.18487
  — STATES OpenAlex W4416381655, `cited_by_count: 0`, preprint
  only, no journal. Does NOT list citing works.
- https://inspirehep.net/api/literature?q=arxiv:2504.18487 —
  STATES zero hits (HPS is not in INSPIRE yet). Does NOT give
  citations.
- https://inspirehep.net/api/literature?q=refersto:arxiv:2504.18487
  — Returned unrelated records (query not a usable citation
  graph for this preprint). Does NOT identify a citing paper
  on excess charge.
- https://scholar.google.com/scholar?cites=13552851381728662902
  — Google bot-block this session. STATES nothing usable.
- arXiv API `all:2504.18487` — only 2504.18487v1 itself.
- arXiv API `ti:"excess charge" AND abs:atoms` — 11 hits; the
  only ones dated after 25 Apr 2025 are 2504.18487v1 and
  2511.07582v1 (bosonic, 1.4811). 2207.08328v2 is a comment
  update of a 2022 paper, not a new theorem.
- arXiv API `all:"excess charge" AND all:fermion` in
  2025-04-01..2026-08-28 — only 2504.18487v1.
- arXiv API `all:"N_c" AND all:"Z^{1/3}"` in that window —
  only 2504.18487v1.
- arXiv API `all:"1.1185" AND all:ionization` — 0 hits
  (LaTeX splitting; the HTML of HPS itself has the number).
- arXiv API `au:Hundertmark` after 2025-04-25 — no second
  ionization / excess-charge paper (2602.04685 is ultracontractivity,
  unrelated).
- arXiv API `au:Benguria` 2022–2026 — 2207.08328v2 (errors),
  2502.15444 (TFW), 2511.07582 (bosonic 1.4811), 2201.13421
  (Hartree). None beat 1.1185 for fermions.

Failed / blocked this session (logged): APS PRA 29, 3018 full
text (Cloudflare); 2207.08328v2 PDF and official HTML (404);
Google Scholar citing page (bot-block); OpenAlex
`/works/https://arxiv.org/abs/2504.18487` (404; the doi filter
worked instead).

---

## Nam EMS newsletter (opened as a lead check)

- https://ems.press/content/serial-article-files/12081?nt=1 —
  Nam “The Ionization Problem”. STATES then-best explicit
  \(\min(2Z+1,\,1.22Z+3Z^{1/3})\); Lieb proof sketch; FS/SSS
  \(Z+O(Z^{5/7})\) “no further improvement in the past three
  decades” (pre-HPS). Does NOT cite 1.1185; does NOT prove
  bounded excess.

---

## Record line (what to beat)

Published fermionic Schrödinger, non-asymptotic, leading term:

\[
N_c(Z)<1.1185\,Z+4Z^{1/3}\qquad(Z\ge 4),
\]

Hundertmark–Pattakos–Schulz, arXiv:2504.18487**v1**, 25 Apr 2025.
Sharper printed form: Prop. 2.5 with \(b(3)\in(1.1184,1.1185)\)
and remainder \(3.90Z^{1/3}+\cdots\). For \(2\le Z\le 35\),
Prop. 2.4 \(b(2)Z+2.96Z^{1/3}\) can be the better HPS line;
Lieb \(2Z+1\) still wins at small \(Z\).

Nothing later than that v1, among papers opened this session,
improves the leading 1.1185, proves \(N_0(Z)-Z\) bounded, or
gives a better published remainder class.

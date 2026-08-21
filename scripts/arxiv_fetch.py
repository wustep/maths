#!/usr/bin/env python3
"""Fetch an arXiv paper's metadata and full text; flag bound-looking claims.

Usage:
  python3 scripts/arxiv_fetch.py 2211.09055
  python3 scripts/arxiv_fetch.py https://arxiv.org/abs/2509.05260v3 --text pdf
  python3 scripts/arxiv_fetch.py 2211.11731 --research problems/union-closed/RESEARCH.md

Prints title, authors, date, abstract, comment, then a heuristic list of
sentences from the full text that look like claimed bounds (contain ≤/≥,
"we prove", "lower bound", "improves", ...). Those lines are leads, not
citations — read the paper before trusting a number.

--text auto|html|pdf|none   full-text source (default auto: HTML, then PDF)
--keep-pdf PATH             also save the fetched PDF (e.g. compute/refs/x.pdf)
--research PATH             append a RESEARCH.md-style stub with the abs URL

Stdlib only; PDF extraction shells out to pdftotext.
"""

import argparse
import datetime
import html.parser
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import xml.etree.ElementTree as ET

UA = "maths-research-helper/1.0 (https://github.com/wustep/maths)"
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"

BOUND_RE = re.compile(
    r"(≤|≥|≲|≳|\\le[qs]?\b|\\ge[qs]?\b|\\lesssim|\\gtrsim"
    r"|\bwe (?:prove|show|obtain|establish|improve)\b"
    r"|\b(?:lower|upper) bound\b|\bbest known\b|\bimprov(?:e|es|ed|ing|ement)\b"
    r"|\bprevious(?:ly)? (?:best|record)\b)",
    re.IGNORECASE,
)


def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_id(raw):
    """Accept 2211.09055, 2211.09055v2, math/0211159, arXiv: prefix, or abs/pdf/html URL."""
    s = raw.strip()
    s = re.sub(r"^(https?://(www\.)?arxiv\.org/(abs|pdf|html)/|arxiv:)", "", s, flags=re.I)
    s = re.sub(r"(\.pdf)?/?$", "", s)
    if not re.fullmatch(r"(\d{4}\.\d{4,5}|[a-z-]+(\.[A-Z]{2})?/\d{7})(v\d+)?", s):
        sys.exit(f"error: {raw!r} does not look like an arXiv id")
    return s


def get_metadata(arxiv_id):
    xml = fetch(f"https://export.arxiv.org/api/query?id_list={arxiv_id}&max_results=1")
    entry = ET.fromstring(xml).find(f"{ATOM}entry")
    if entry is None or entry.find(f"{ATOM}id") is None:
        sys.exit(f"error: arXiv API returned no entry for {arxiv_id}")
    text = lambda el, tag, ns=ATOM: re.sub(r"\s+", " ", (entry.findtext(f"{ns}{tag}") or "").strip())
    versioned = entry.findtext(f"{ATOM}id").split("/abs/", 1)[-1]
    return {
        "id": re.sub(r"v\d+$", "", versioned),
        "versioned_id": versioned,
        "title": text(entry, "title"),
        "abstract": text(entry, "summary"),
        "authors": [a.findtext(f"{ATOM}name") for a in entry.findall(f"{ATOM}author")],
        "updated": text(entry, "updated"),
        "comment": text(entry, "comment", ARXIV),
    }


class HTMLText(html.parser.HTMLParser):
    """Extract text from arXiv's LaTeXML HTML; use <math alttext> for formulas."""

    SKIP = {"script", "style", "head", "nav"}
    BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr", "figcaption", "section"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.depth = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP or tag == "math":
            self.depth += 1
        if tag == "math":
            alt = dict(attrs).get("alttext")
            if alt:
                self.parts.append(f" ${alt}$ ")

    def handle_endtag(self, tag):
        if tag in self.SKIP or tag == "math":
            self.depth = max(0, self.depth - 1)
        if tag in self.BLOCK:
            self.parts.append("\n\n")

    def handle_data(self, data):
        if not self.depth:
            self.parts.append(data)


def get_fulltext(meta, mode, keep_pdf):
    vid = meta["versioned_id"]
    if mode in ("auto", "html"):
        time.sleep(3)  # arXiv asks for >=3s between requests
        try:
            parser = HTMLText()
            parser.feed(fetch(f"https://arxiv.org/html/{vid}").decode("utf-8", "replace"))
            return "".join(parser.parts), f"https://arxiv.org/html/{vid}"
        except Exception as e:
            if mode == "html":
                sys.exit(f"error: HTML fetch failed ({e}); try --text pdf")
            print(f"[html unavailable ({e}); falling back to pdf]", file=sys.stderr)
    time.sleep(3)
    pdf = fetch(f"https://arxiv.org/pdf/{vid}")
    path = keep_pdf or tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
    with open(path, "wb") as f:
        f.write(pdf)
    if keep_pdf:
        print(f"[saved PDF to {keep_pdf}]", file=sys.stderr)
    out = subprocess.run(["pdftotext", path, "-"], capture_output=True, check=True)
    return out.stdout.decode("utf-8", "replace"), f"https://arxiv.org/pdf/{vid}"


def bound_sentences(text, limit=25):
    sentences = []
    for para in re.split(r"\n\s*\n", text):
        para = re.sub(r"\s+", " ", para).strip()
        sentences += re.split(r"(?<=[.!?])\s+(?=[A-Z\d\\$(])", para)
    seen, hits = set(), []
    for s in sentences:
        if 20 <= len(s) and BOUND_RE.search(s) and s not in seen:
            seen.add(s)
            hits.append(s if len(s) <= 300 else s[:297] + "...")
    return hits[:limit], len(hits)


def research_stub(meta):
    last = [a.rsplit(None, 1)[-1] for a in meta["authors"] if a]
    names = "–".join(last) if len(last) <= 6 else f"{last[0]} et al."
    d = datetime.date.fromisoformat(meta["updated"][:10])
    date = f"{d.day} {d.strftime('%b %Y')}"
    return (
        f"- [{names}, *{meta['title']}*, arXiv:{meta['versioned_id']}]"
        f"(https://arxiv.org/abs/{meta['id']}) ({date}). TODO: claimed result; verified how?"
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("id", help="arXiv id or abs/pdf/html URL")
    ap.add_argument("--text", choices=["auto", "html", "pdf", "none"], default="auto")
    ap.add_argument("--keep-pdf", metavar="PATH", help="save the fetched PDF here")
    ap.add_argument("--research", metavar="PATH", help="append a stub to this RESEARCH.md")
    args = ap.parse_args()

    meta = get_metadata(parse_id(args.id))
    print(f"arXiv:{meta['versioned_id']}  https://arxiv.org/abs/{meta['id']}")
    print(f"Title:    {meta['title']}")
    print(f"Authors:  {', '.join(meta['authors'])}")
    print(f"Updated:  {meta['updated'][:10]}")
    if meta["comment"]:
        print(f"Comment:  {meta['comment']}")
    print(f"\nAbstract:\n{meta['abstract']}\n")

    if args.text != "none":
        text, source = get_fulltext(meta, args.text, args.keep_pdf)
        hits, total = bound_sentences(text)
        print(f"Bound-looking sentences (heuristic, from {source} — verify in the paper):")
        for h in hits:
            print(f"  * {h}")
        if total > len(hits):
            print(f"  ... {total - len(hits)} more matches not shown")
        if not hits:
            print("  (none matched — read the paper directly)")

    if args.research:
        stub = research_stub(meta)
        with open(args.research, "r+", encoding="utf-8") as f:
            body = f.read()
            if meta["id"] in body:
                print(f"\n[{args.research} already mentions arXiv:{meta['id']}; stub not appended]")
            else:
                f.write(("" if body.endswith("\n") else "\n") + stub + "\n")
                print(f"\nAppended to {args.research}:\n{stub}")


if __name__ == "__main__":
    main()

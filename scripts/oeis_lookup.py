#!/usr/bin/env python3
"""Look up an OEIS sequence by A-number or by terms.

Usage:
  python3 scripts/oeis_lookup.py A000045
  python3 scripts/oeis_lookup.py 1,2,4,8,16,32,64

Prints A-number, name, first terms, and the oeis.org URL for the top
matches. Stdlib only (OEIS JSON API).
"""

import json
import re
import sys
import urllib.parse
import urllib.request

UA = "maths-research-helper/1.0 (https://github.com/wustep/maths)"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.strip())
    query = sys.argv[1].strip().replace(" ", "")
    if re.fullmatch(r"[Aa]\d{6,7}", query):
        query = f"id:{query.upper()}"
    url = f"https://oeis.org/search?q={urllib.parse.quote(query)}&fmt=json"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    results = data.get("results") if isinstance(data, dict) else data
    if not results:
        sys.exit(f"no OEIS match for {sys.argv[1]!r}")
    for seq in results[:3]:
        anum = f"A{seq['number']:06d}"
        terms = ",".join(seq["data"].split(",")[:12])
        print(f"{anum}  {seq['name']}")
        print(f"        {terms},...")
        print(f"        https://oeis.org/{anum}")
    if len(results) > 3:
        print(f"({len(results)} matches shown from the first page; refine the terms)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Apply one enumerator-only change to the pinned, unmodified producer.

The union of {d,2d,...,Nd} over mollifier divisors is exactly the active
support. Given n, the next element is min_d d*(floor(n/d)+1), discarding
values above d*N. Thus the changed loops visit the same active integers in
the same order and perform the same Arb operations on them.
"""
import hashlib
from pathlib import Path
import sys

source=Path(__file__).parent/"vendor/finite_original.c"
raw=source.read_bytes()
if hashlib.sha256(raw).hexdigest() != "580d0b51165da58d4ca22e16d80a8c3db603dd0d9246f26dd027b5f820bf0808":
    raise SystemExit("FAIL: unexpected original source")
text=raw.decode()
needle="for(ulong n=2; n<=D*N; n++)"
if text.count(needle)!=3:
    raise SystemExit("FAIL: expected exactly three support scans")
helper='''
/* q2: enumerate the same support in increasing order, without scanning
   inactive integers. The parameter ranges keep all products below 2^64. */
static ulong next_active(ulong n, ulong N, const mollset_t *ms) {
    ulong result = (ulong)-1;
    for (int i=0; i<ms->nd; i++) {
        ulong d=ms->dvec[i], m=n/d+1;
        if (m<=N && d*m<result) result=d*m;
    }
    return result;
}
'''
text=text.replace("static void bt_eval",helper+"\nstatic void bt_eval",1)
text=text.replace(needle,"for(ulong n=2; n<=D*N; n=next_active(n,N,&ms))")
Path(sys.argv[1]).write_text(text)

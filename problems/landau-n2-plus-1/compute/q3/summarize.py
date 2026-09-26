#!/usr/bin/env python3
"""Build n2p1.json from C lists in this directory. Streams the P2 file."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from n2p1_lib import (  # noqa: E402
    C_Q,
    bateman_horn_integral,
    landau_shanks_product,
    primes_upto,
    wolf_prediction_li,
)
from sieve_n2p1 import checkpoints  # noqa: E402

HERE = Path(__file__).resolve().parent


def sha256_file(path: Path, buf: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(buf)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def iter_n(path: Path):
    with path.open() as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            yield int(s.split()[0])


def load_n(path: Path) -> list[int]:
    return list(iter_n(path))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=HERE)
    args = parser.parse_args()
    d = args.dir.resolve()
    meta_path = d / "sieve_meta.json"
    if not meta_path.is_file():
        sys.exit(f"missing {meta_path}")
    meta = json.loads(meta_path.read_text())
    n_max = int(meta["n_max"])
    prime_n = load_n(d / "prime_n.txt")
    p2 = load_n(d / "p2_omega2.txt")
    if len(prime_n) != int(meta["count_prime"]):
        sys.exit(f"prime count mismatch list={len(prime_n)} meta={meta['count_prime']}")
    if len(p2) != int(meta["count_p2_omega_eq_2_composite"]):
        sys.exit(f"p2 count mismatch list={len(p2)} meta={meta['count_p2_omega_eq_2_composite']}")

    bh_int = bateman_horn_integral(n_max)
    bh = C_Q * bh_int
    wolf_li = wolf_prediction_li(n_max)
    cprod = landau_shanks_product(primes_upto(min(n_max, 2_000_000)))
    wolf_rows = checkpoints(prime_n, n_max)
    p_path = d / "prime_n.txt"
    p2_path = d / "p2_omega2.txt"

    ns = []
    for e in range(3, 9):
        ns.append(10**e)
        if e < 8:
            ns.append(2 * 10**e)
            ns.append(5 * 10**e)
    ns = sorted({n for n in ns if n <= n_max} | {n_max})
    comparison_rows = []
    for N in ns:
        c_pr = sum(1 for n in prime_n if n <= N)
        c_p2 = sum(1 for n in p2 if n <= N)
        bhN = C_Q * bateman_horn_integral(N)
        wli = wolf_prediction_li(N)
        shape = N / (math.log(N) ** 1.5)
        comparison_rows.append(
            {
                "N": N,
                "primes": c_pr,
                "p2_composite": c_p2,
                "iwaniec_p2": c_pr + c_p2,
                "bateman_horn": bhN,
                "wolf_li": wli,
                "prime_over_bh": c_pr / bhN,
                "prime_over_wolf_li": c_pr / wli,
                "iwaniec_p2_over_shape": (c_pr + c_p2) / shape,
            }
        )

    payload = {
        "n_max": n_max,
        "count_prime": len(prime_n),
        "count_p2_omega_eq_2_composite": len(p2),
        "count_iwaniec_p2": len(prime_n) + len(p2),
        "count_omega_le2_composite_diagnostic": meta["count_omega_le2_composite_diagnostic"],
        "unsplit": meta["unsplit"],
        "omega_hist": meta["omega_hist"],
        "first_prime_n": prime_n[:30],
        "first_prime_values": [n * n + 1 for n in prime_n[:30]],
        "last_prime_n": prime_n[-8:],
        "last_prime_values": [n * n + 1 for n in prime_n[-8:]],
        "first_p2_n": p2[:12],
        "C_q_published": C_Q,
        "C_q_truncated_product": cprod,
        "bateman_horn_integral": bh_int,
        "bateman_horn_prediction": bh,
        "wolf_li_prediction": wolf_li,
        "prime_over_bh": (len(prime_n) / bh) if bh else None,
        "prime_over_wolf_li": (len(prime_n) / wolf_li) if wolf_li else None,
        "iwaniec_shape_N_over_logN_3_2": n_max / (math.log(n_max) ** 1.5),
        "wolf_A083844": wolf_rows,
        "seconds_roots": meta.get("seconds_sieve"),
        "seconds_sieve_classify": meta.get("seconds_classify"),
        "rss_kb": meta.get("rss_kb"),
        "producer": meta.get("producer"),
        "note": (
            "prime_n: n=1 and even n with n^2+1 prime by deterministic MR "
            "(bases 2,3,5,7,11,13,17,19,23; OEIS A014233). "
            "Iwaniec P2 means Ω(n^2+1)<=2 (multiplicity). "
            "n^2+1 is never a square for n>=1, so Ω=2 means a product of two primes. "
            "P2 list is complete on 1<=n<=n_max. Not a proof of infinitude. "
            "Did not beat Wolf/Grantham published complete lists."
        ),
        "prime_n_txt": p_path.name,
        "p2_txt": p2_path.name,
        "prime_n_sha256": sha256_file(p_path),
        "p2_sha256": sha256_file(p2_path),
        "prime_n_bytes": p_path.stat().st_size,
        "p2_bytes": p2_path.stat().st_size,
        "comparison_rows": comparison_rows,
    }
    out = d / "n2p1.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    (d / "comparison.json").write_text(
        json.dumps({"n_max": n_max, "rows": comparison_rows}, indent=2) + "\n"
    )
    print(f"wrote {out}")
    print(
        f"n_max={n_max} primes={len(prime_n)} p2={len(p2)} "
        f"BH={bh:.3f} ratio={payload['prime_over_bh']:.6f}"
    )
    print("wolf rows", wolf_rows)
    mismatches = [row for row in wolf_rows if not row["match"]]
    if mismatches:
        sys.exit(f"Wolf mismatch: {mismatches}")
    if payload["unsplit"]:
        sys.exit(f"unsplit leftovers: {payload['unsplit']}")
    if n_max >= 100_000_000 and len(prime_n) != 3_954_181:
        sys.exit(f"prime count {len(prime_n)} != Wolf π_q(10^16)=3954181")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Published upper envelopes for Nc(Z), integer Z = 1..200.

Not a new bound. Replays the printed inequalities:

  Lieb:            Nc <= floor(2Z)   (Nc < 2Z+1, Nc integer)
  Nam:             Nc < 1.22 Z + 3 Z^{1/3}
  HPS s=2 (Z>=2):  Nc < b(2) Z + 2.96 Z^{1/3}
  HPS s=3 (Z>=4):  Nc < b(3) Z + 3.90 Z^{1/3}
                   + 0.0134 + 0.184 Z^{-1/3} + 0.0196 Z^{-2/3}
  HPS simplified:  Nc < 1.1185 Z + 4 Z^{1/3}   (Z>=4)

Sources: Lieb, Phys. Rev. A 29 (1984); Nam, arXiv:1009.2367v3;
Hundertmark–Pattakos–Schulz, arXiv:2504.18487v1 Prop. 2.4–2.5.

Writes certs/best_published.json and, if matplotlib is available,
figures/bounds.png and figures/bounds.svg. Cross-checks C/Rust dumps
when those files exist.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERTS = HERE / "certs"
FIGS = HERE.parent.parent / "figures"


def b2_closed() -> float:
    return 0.5 * (math.sqrt(2.0) + 1.0)


def b3_closed() -> float:
    one_plus = 1.0 + math.sqrt(2.0)
    return (2.0 / 3.0) * (one_plus ** (1.0 / 3.0)) / (one_plus ** (2.0 / 3.0) - 1.0)


def lieb(z: int) -> float:
    return math.floor(2.0 * z)


def nam(z: int) -> float:
    return 1.22 * z + 3.0 * z ** (1.0 / 3.0)


def hps_s2(z: int, b2: float) -> float:
    return b2 * z + 2.96 * z ** (1.0 / 3.0)


def hps_s3(z: int, b3: float) -> float:
    z13 = z ** (1.0 / 3.0)
    return b3 * z + 3.90 * z13 + 0.0134 + 0.184 / z13 + 0.0196 / (z13 * z13)


def hps_simplified(z: int) -> float:
    return 1.1185 * z + 4.0 * z ** (1.0 / 3.0)


def envelopes(z: int, b2: float, b3: float) -> dict:
    row = {
        "Z": z,
        "lieb": lieb(z),
        "nam": nam(z),
        "hps_s2": hps_s2(z, b2) if z >= 2 else None,
        "hps_s3": hps_s3(z, b3) if z >= 4 else None,
        "hps_simplified": hps_simplified(z) if z >= 4 else None,
    }
    candidates = [("lieb", row["lieb"]), ("nam", row["nam"])]
    if row["hps_s2"] is not None:
        candidates.append(("hps_s2", row["hps_s2"]))
    if row["hps_s3"] is not None:
        candidates.append(("hps_s3", row["hps_s3"]))
    if row["hps_simplified"] is not None:
        candidates.append(("hps_simplified", row["hps_simplified"]))
    name, best = min(candidates, key=lambda kv: kv[1])
    row["best_published"] = best
    row["best_name"] = name
    return row


def parse_ld(s: str) -> float:
    return float(s.strip())


def load_c_json() -> dict | None:
    path = CERTS / "b3_c.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def load_rs_json() -> dict | None:
    path = CERTS / "b3_rs.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text())


def check_language_dumps(b2: float, b3: float) -> dict:
    """C closed form vs Rust ternary/grid. Agreement is the second check."""
    out = {"c_present": False, "rs_present": False, "agree": None}
    c = load_c_json()
    rs = load_rs_json()
    if c:
        out["c_present"] = True
        cb2 = parse_ld(c["b2"])
        cb3 = parse_ld(c["b3"])
        if abs(cb2 - b2) > 1e-14:
            raise SystemExit(f"C b2 {cb2} disagrees with Python {b2}")
        if abs(cb3 - b3) > 1e-14:
            raise SystemExit(f"C b3 {cb3} disagrees with Python {b3}")
        out["b2_c"] = cb2
        out["b3_c"] = cb3
    if rs:
        out["rs_present"] = True
        rb3 = parse_ld(rs["b3_ternary"])
        rb2 = parse_ld(rs["b2_ternary"])
        rb3c = parse_ld(rs["b3_closed"])
        if abs(rb3 - b3) > 1e-12:
            raise SystemExit(f"Rust ternary b3 {rb3} disagrees with Python {b3}")
        if abs(rb3c - b3) > 1e-14:
            raise SystemExit(f"Rust closed b3 {rb3c} disagrees with Python {b3}")
        if abs(rb2 - b2) > 1e-12:
            raise SystemExit(f"Rust ternary b2 {rb2} disagrees with Python {b2}")
        out["b2_rs_ternary"] = rb2
        out["b3_rs_ternary"] = rb3
        out["b3_rs_closed"] = rb3c
    if c and rs:
        if abs(parse_ld(c["b3"]) - parse_ld(rs["b3_ternary"])) > 1e-12:
            raise SystemExit("C and Rust disagree on b(3)")
        if abs(parse_ld(c["b2"]) - parse_ld(rs["b2_ternary"])) > 1e-12:
            raise SystemExit("C and Rust disagree on b(2)")
        out["agree"] = True
        print("C closed form and Rust ternary/grid agree on b(2), b(3)")
    return out


def check_c_csv(rows: list[dict]) -> None:
    path = CERTS / "bound_table.csv"
    if not path.is_file():
        return
    with path.open() as f:
        got = list(csv.DictReader(f))
    if len(got) != len(rows):
        raise SystemExit(f"CSV row count {len(got)} != {len(rows)}")
    for a, b in zip(rows, got):
        if int(b["Z"]) != a["Z"]:
            raise SystemExit("CSV Z mismatch")
        for key in ("lieb", "nam", "best_published"):
            if abs(float(b[key]) - a[key]) > 5e-12:
                raise SystemExit(f"CSV {key} Z={a['Z']}: {b[key]} vs {a[key]}")
        for key in ("hps_s2", "hps_s3", "hps_simplified"):
            raw = (b.get(key) or "").strip()
            if a[key] is None:
                if raw:
                    raise SystemExit(f"CSV {key} should be empty at Z={a['Z']}")
            else:
                if abs(float(raw) - a[key]) > 5e-12:
                    raise SystemExit(f"CSV {key} Z={a['Z']}: {raw} vs {a[key]}")
        if b["best_name"] != a["best_name"]:
            raise SystemExit(
                f"CSV best_name Z={a['Z']}: {b['best_name']} vs {a['best_name']}"
            )
    print("certs/bound_table.csv agrees with Python envelopes")


def write_csv(rows: list[dict]) -> None:
    path = CERTS / "bound_table.csv"
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "Z",
                "lieb",
                "nam",
                "hps_s2",
                "hps_s3",
                "hps_simplified",
                "best_published",
                "best_name",
            ]
        )
        for r in rows:
            def fmt(x):
                return "" if x is None else f"{x:.18f}"

            w.writerow(
                [
                    r["Z"],
                    fmt(r["lieb"]),
                    fmt(r["nam"]),
                    fmt(r["hps_s2"]),
                    fmt(r["hps_s3"]),
                    fmt(r["hps_simplified"]),
                    fmt(r["best_published"]),
                    r["best_name"],
                ]
            )
    print("wrote", path)


def first_crossover(rows: list[dict], left: str, right: str) -> int | None:
    for r in rows:
        lv, rv = r[left], r[right]
        if lv is None or rv is None:
            continue
        if lv < rv:
            return r["Z"]
    return None


def plot_bounds(rows: list[dict], z_nam: int | None, z_lieb: int | None) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib missing; skip figures")
        return

    FIGS.mkdir(parents=True, exist_ok=True)
    zs = [r["Z"] for r in rows]

    def col(name):
        return [r[name] for r in rows]

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    ax.plot(zs, col("lieb"), color="#555555", lw=1.2, label=r"Lieb $\lfloor 2Z\rfloor$")
    ax.plot(zs, col("nam"), color="#1f4e79", lw=1.2, label=r"Nam $1.22Z+3Z^{1/3}$")
    ax.plot(
        [r["Z"] for r in rows if r["hps_s2"] is not None],
        [r["hps_s2"] for r in rows if r["hps_s2"] is not None],
        color="#2a7f62",
        lw=1.2,
        label=r"HPS $s=2$",
    )
    ax.plot(
        [r["Z"] for r in rows if r["hps_s3"] is not None],
        [r["hps_s3"] for r in rows if r["hps_s3"] is not None],
        color="#a31f34",
        lw=1.4,
        label=r"HPS $s=3$ Prop. 2.5",
    )
    ax.plot(
        [r["Z"] for r in rows if r["hps_simplified"] is not None],
        [r["hps_simplified"] for r in rows if r["hps_simplified"] is not None],
        color="#b36b00",
        lw=1.0,
        ls="--",
        label=r"HPS $1.1185Z+4Z^{1/3}$",
    )
    ax.plot(
        zs,
        col("best_published"),
        color="#111111",
        lw=0.8,
        ls=":",
        label="best published",
    )
    if z_nam is not None:
        ax.axvline(z_nam, color="#a31f34", ls=":", lw=0.8, alpha=0.7)
    if z_lieb is not None:
        ax.axvline(z_lieb, color="#555555", ls=":", lw=0.8, alpha=0.7)
    ax.set_xlabel("nuclear charge $Z$")
    ax.set_ylabel(r"published upper envelope on $N_c(Z)$")
    ax.set_title("Published bounds only — not a new bound")
    ax.legend(frameon=False, fontsize=8)
    ax.set_xlim(1, 200)
    fig.tight_layout()
    png = FIGS / "bounds.png"
    svg = FIGS / "bounds.svg"
    fig.savefig(png, dpi=140)
    fig.savefig(svg)
    print("wrote", png)
    print("wrote", svg)


def main() -> None:
    CERTS.mkdir(parents=True, exist_ok=True)
    b2 = b2_closed()
    b3 = b3_closed()
    print(f"b2 = {b2:.21f}")
    print(f"b3 = {b3:.21f}")
    if not (1.1184 < b3 < 1.1185):
        raise SystemExit(f"b3={b3} not in (1.1184, 1.1185)")
    if not (1.2071 < b2 < 1.2072):
        raise SystemExit(f"b2={b2} not in (1.2071, 1.2072)")

    rows = [envelopes(z, b2, b3) for z in range(1, 201)]
    lang = check_language_dumps(b2, b3)
    check_c_csv(rows)
    write_csv(rows)

    z_nam = first_crossover(rows, "hps_s3", "nam")
    z_lieb = first_crossover(rows, "hps_s3", "lieb")
    z_s2 = first_crossover(rows, "hps_s3", "hps_s2")
    print(f"smallest Z where HPS s=3 beats Nam:  {z_nam}")
    print(f"smallest Z where HPS s=3 beats Lieb: {z_lieb}")
    print(f"smallest Z where HPS s=3 beats HPS s=2: {z_s2}")

    blob = {
        "not_a_new_bound": True,
        "record": "Hundertmark–Pattakos–Schulz arXiv:2504.18487v1",
        "also": ["Lieb Phys. Rev. A 29 (1984)", "Nam arXiv:1009.2367v3"],
        "constants": {
            "b2": b2,
            "b3": b3,
            "b3_interval": [1.1184, 1.1185],
            "b2_interval": [1.2071, 1.2072],
        },
        "applicability": {
            "lieb": "all Z",
            "nam": "all Z",
            "hps_s2": "Z >= 2",
            "hps_s3": "Z >= 4",
            "hps_simplified": "Z >= 4",
        },
        "crossovers": {
            "hps_s3_beats_nam_smallest_Z": z_nam,
            "hps_s3_beats_lieb_smallest_Z": z_lieb,
            "hps_s3_beats_hps_s2_smallest_Z": z_s2,
        },
        "language_check": lang,
        "envelopes": rows,
    }
    out = CERTS / "best_published.json"
    out.write_text(json.dumps(blob, indent=2) + "\n")
    print("wrote", out)
    plot_bounds(rows, z_nam, z_lieb)
    print("compare_bounds.py PASS")


if __name__ == "__main__":
    main()

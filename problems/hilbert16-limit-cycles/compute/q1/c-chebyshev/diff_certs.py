#!/usr/bin/env python3
"""Diff the Python and Rust certificate cores."""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, "certs")


def load(name: str) -> dict:
    path = os.path.join(CERTS, name)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def fail(msg: str) -> None:
    print(f"diff_certs FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def mono_key(m: dict) -> tuple:
    return (int(m["u"]), int(m["v"]), int(m["num"]), int(m["den"]))


def main() -> None:
    py = load("core.json")
    rs = load("rust_core.json")

    scalar_keys = [
        "deg_Y",
        "deg_Yu",
        "deg_Yv",
        "deg_X",
        "conjugacy",
        "H11_from_this_field",
        "beats_HanLi_153",
        "nine_ovals",
        "table1_L_Ch_match",
    ]
    for key in scalar_keys:
        if py[key] != rs[key]:
            fail(f"{key}: python {py[key]!r} != rust {rs[key]!r}")

    for key in ("T3_at_1", "T3_at_-1", "T3_at_1/2", "T3_at_-1/2"):
        if py[key] != rs[key]:
            fail(f"{key}: python {py[key]!r} != rust {rs[key]!r}")

    if py["L_Ch"] != rs["L_Ch"]:
        fail(f"L_Ch mismatch\n  python {py['L_Ch']}\n  rust {rs['L_Ch']}")
    if py["beats_four"] != rs["beats_four"]:
        fail(f"beats_four: {py['beats_four']} vs {rs['beats_four']}")
    if py["four"] != rs["four"]:
        fail(f"four: {py['four']} vs {rs['four']}")

    for name in ("Y_u_monomials", "Y_v_monomials"):
        a = sorted(mono_key(m) for m in py[name])
        b = sorted(mono_key(m) for m in rs[name])
        if a != b:
            only_py = set(a) - set(b)
            only_rs = set(b) - set(a)
            fail(f"{name} mismatch\n  only python {sorted(only_py)}\n  only rust {sorted(only_rs)}")

    if py["T_m"] != {k: rs["T_m"][k] for k in py["T_m"]}:
        fail(f"T_m mismatch\n  python {py['T_m']}\n  rust {rs['T_m']}")

    table_py = load("table_replay.json")
    table_rs = load("rust_table.json")
    py_all = {int(k): v for k, v in table_py["all_N_le_50_with_L_Ch"].items()}
    rs_all = {int(k): v for k, v in table_rs["L_Ch_N_le_50"].items()}
    if py_all != rs_all:
        keys = sorted(set(py_all) | set(rs_all))
        diffs = [(n, py_all.get(n), rs_all.get(n)) for n in keys if py_all.get(n) != rs_all.get(n)]
        fail(f"N<=50 L_Ch mismatch: {diffs}")

    print("diff_certs: ok")
    print(f"  deg Y = {py['deg_Y']}")
    print(f"  nine ovals = {py['nine_ovals']}")
    print(f"  Table 1 L_Ch match = {py['table1_L_Ch_match']}")
    print(f"  beats four = {py['beats_four']}")
    print(f"  Y_u monomials = {len(py['Y_u_monomials'])}")
    print(f"  Y_v monomials = {len(py['Y_v_monomials'])}")


if __name__ == "__main__":
    main()

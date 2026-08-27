"""Copy independently checked tri_done rows from another thick_out.

Only rows with evals == 46 * 2^rank and complete=true are imported.
Does not write new_schemes.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEST = HERE / "thick_out"


def expected_evals(rank: int) -> int:
    return 46 * (1 << rank)


def main() -> None:
    src = Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "q2" / "thick_out")
    DEST.mkdir(exist_ok=True)
    dest_path = DEST / "h_imp.jsonl"
    have = set()
    if dest_path.exists():
        for line in dest_path.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                have.add((r["cert"], r.get("radius", 1)))
    n = 0
    with dest_path.open("a") as out:
        for path in sorted(src.glob("h*.jsonl")):
            if path.name.endswith("_novel.jsonl"):
                continue
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                rec = json.loads(line)
                if rec.get("kind") != "tri_done":
                    continue
                if rec.get("rank", 0) < 22:
                    continue
                exp = expected_evals(rec["rank"])
                if not rec.get("complete") or rec.get("evals") != exp:
                    continue
                key = (rec["cert"], rec.get("radius", 1))
                if key in have:
                    continue
                out.write(json.dumps(rec) + "\n")
                have.add(key)
                n += 1
                print("imported", rec["cert"], "rank", rec["rank"],
                      "evals", rec["evals"], "novel", rec.get("novel"))
    print(f"imported {n} complete leftover rows into {dest_path}")


if __name__ == "__main__":
    main()

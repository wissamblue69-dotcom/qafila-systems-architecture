from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

FIELDS = ["fixture_id", "policy_version", "status", "hold_reason", "payload_hash", "receipt_hash", "network_egress"]


def load(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sorted(csv.DictReader(handle), key=lambda row: row["fixture_id"])


def projected(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [{field: row[field] for field in FIELDS} for row in rows]


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare deterministic Qafila benchmark runs")
    parser.add_argument("--left", required=True, type=Path)
    parser.add_argument("--right", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    left = projected(load(args.left))
    right = projected(load(args.right))
    result = {"matches": left == right, "fields": FIELDS, "left": left, "right": right}
    args.out.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"matches": result["matches"], "row_count": len(left)}, ensure_ascii=False))
    return 0 if result["matches"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

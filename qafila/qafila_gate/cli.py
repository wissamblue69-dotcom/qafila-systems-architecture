from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qafila_gate.checker import iter_fixtures, load_json, validate_event, write_benchmark, write_jsonl


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Qafila deterministic governance gate (local dry-run)")
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--artifacts", required=True, type=Path)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--run-label", required=True)
    parser.add_argument("--expect", choices=["allow", "hold", "mixed"], default="mixed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.fixtures.is_dir():
        print(f"fixtures directory not found: {args.fixtures}", file=sys.stderr)
        return 2
    fixtures = sorted(args.fixtures.glob("*.json"))
    if not fixtures:
        print(f"no JSON fixtures found: {args.fixtures}", file=sys.stderr)
        return 2
    args.artifacts.mkdir(parents=True, exist_ok=True)
    policy = load_json(args.policy)
    findings = []
    for fixture_id, event, operation in iter_fixtures(fixtures):
        findings.append(validate_event(event, policy, fixture_id, operation))

    holds = [finding.as_dict() for finding in findings if finding.status == "hold"]
    all_findings = [finding.as_dict() for finding in findings]
    write_jsonl(args.artifacts / "hold_register.jsonl", holds)
    write_jsonl(args.artifacts / "gate_results.jsonl", all_findings)
    write_benchmark(args.artifacts / "benchmark.csv", args.experiment_id, findings, args.run_label)

    summary = {
        "experiment_id": args.experiment_id,
        "run_label": args.run_label,
        "policy_version": policy["policy_version"],
        "fixture_count": len(findings),
        "allow_count": sum(finding.status == "allow" for finding in findings),
        "hold_count": sum(finding.status == "hold" for finding in findings),
        "network_egress": policy.get("network_egress"),
        "expected": args.expect,
        "passed": (
            args.expect == "mixed"
            or (args.expect == "allow" and all(finding.status == "allow" for finding in findings))
            or (args.expect == "hold" and all(finding.status == "hold" for finding in findings))
        ),
    }
    with (args.artifacts / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a Qafila context run receipt from tracked local sources")
    parser.add_argument("--repo-commit", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    source_paths = [
        Path("qafila/coordination/README.md"),
        Path("qafila/coordination/review_capsules/GEMINI_REVIEW_CAPSULE.md"),
        Path("qafila/coordination/verification/verification_test.v1.json"),
        Path("qafila/docs/gh01-gh02-local-results.md"),
        Path(".github/workflows/deterministic-gate.yml"),
        Path("DRAFT_PR_REVIEW.md"),
        Path("qafila/policy/governance-policy.v1.json"),
    ]
    sources = []
    for relative_path in source_paths:
        absolute_path = root / relative_path
        if not absolute_path.is_file():
            raise SystemExit(f"missing receipt source: {relative_path}")
        sources.append({"path": str(relative_path), "source_hash": sha256_file(absolute_path)})

    receipt = {
        "schema_version": "qafila-context-run-receipt.v1",
        "receipt_id": "ctxr_qafila_coordination_20260822_001",
        "run_type": "coordination_review_ingest",
        "mode": "experimental_dry_run",
        "repository": "wissamblue69-dotcom/qafila-systems-architecture",
        "base_commit": args.repo_commit,
        "policy_version": "qafila-governance-policy.v1",
        "review_status": "candidate_review_recorded",
        "external_actions": {
            "git_push": False,
            "pull_request_created": False,
            "branch_protection_changed": False,
            "release_created": False,
            "email_sent": False,
        },
        "sources": sources,
        "assertions": [
            {"claim_ref": "GH-01", "status": "locally_validated", "scope": "two deterministic local runs"},
            {"claim_ref": "GH-02", "status": "locally_validated", "scope": "ten negative fixtures held"},
            {"claim_ref": "GEMINI_REVIEW", "status": "recorded_as_external_review", "scope": "user-supplied review capsule"},
            {"claim_ref": "DRAFT_PR", "status": "local_only", "scope": "no remote branch or PR exists"},
        ],
    }
    receipt["receipt_hash"] = canonical_hash(receipt)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt_id": receipt["receipt_id"], "receipt_hash": receipt["receipt_hash"], "source_count": len(sources)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

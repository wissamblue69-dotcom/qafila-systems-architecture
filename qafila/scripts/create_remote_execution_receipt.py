from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Record a reviewed Qafila GitHub execution event")
    parser.add_argument("--commit", required=True)
    parser.add_argument("--pr-url", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--artifact-id", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    receipt = {
        "schema_version": "qafila-context-run-receipt.v1",
        "receipt_id": "ctxr_qafila_github_run_32554372127",
        "run_type": "github_draft_pr_governance_gate",
        "mode": "experimental_dry_run",
        "repository": "wissamblue69-dotcom/qafila-systems-architecture",
        "commit_sha": args.commit,
        "pull_request": {"number": 6, "url": args.pr_url, "draft": True, "base_branch": "main"},
        "workflow": {
            "name": "Qafila Deterministic Gate",
            "job_name": "Qafila Governance / deterministic-gate",
            "run_id": args.run_id,
            "run_url": args.run_url,
            "conclusion": "success",
            "artifact_id": args.artifact_id,
            "artifact_name": "qafila-governance-evidence-32554372127"
        },
        "validated_steps": [
            "Verify tracked fixtures are reproducible",
            "GH-01 run A — valid event",
            "GH-01 run B — valid event",
            "GH-02 — negative fail-closed suite",
            "Publish governance evidence",
            "Publish check summary"
        ],
        "external_actions": {
            "branch_pushed": True,
            "draft_pull_request_created": True,
            "branch_protection_changed": False,
            "required_checks_enabled": False,
            "release_created": False,
            "secrets_created": False,
            "github_app_installed": False
        },
        "approval_scope": "User authorized pushing chore/qafila-governance-draft and opening Draft PR #6 only.",
    }
    receipt["receipt_hash"] = canonical_hash(receipt)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt_id": receipt["receipt_id"], "receipt_hash": receipt["receipt_hash"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

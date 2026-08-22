"""Deterministic Qafila governance gate for experimental dry-run validation.

The module deliberately uses only the Python standard library. It performs no network
calls, does not load plugins, and writes evidence only to caller-selected local paths.
"""
from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SHA_PREFIX = "sha256:"
ALLOWED_CONTENT_TYPES = {"note", "source", "claim", "decision", "sync_intent"}
ALLOWED_CLASSIFICATIONS = {"source", "summary", "inference", "proposal", "hypothesis"}
ALLOWED_STATUSES = {"raw", "normalized", "review", "approved", "rejected", "hold"}
ALLOWED_EXTRACTION_METHODS = {"manual", "api", "export", "browser_visible", "fixture"}
EVENT_KEYS = {
    "event_id", "schema_version", "created_at", "source_ref", "actor_ref",
    "correlation_id", "idempotency_key", "content_type", "payload",
    "provenance", "classification", "status",
}
PAYLOAD_KEYS = {"text", "original_term", "normalized_label", "relations", "payload_hash"}
PROVENANCE_KEYS = {"uri", "locator", "extraction_method", "source_hash", "captured_at"}


@dataclass(frozen=True)
class Finding:
    fixture_id: str
    status: str
    hold_reason: str | None
    payload_hash: str | None
    receipt_hash: str
    policy_version: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "status": self.status,
            "hold_reason": self.hold_reason,
            "payload_hash": self.payload_hash,
            "receipt_hash": self.receipt_hash,
            "policy_version": self.policy_version,
        }


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return SHA_PREFIX + hashlib.sha256(canonical_bytes(value)).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_sha256(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith(SHA_PREFIX):
        return False
    digest = value[len(SHA_PREFIX):]
    return len(digest) == 64 and all(char in "0123456789abcdef" for char in digest)


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def hold(policy: dict[str, Any], fixture_id: str, reason: str, payload_hash: str | None) -> Finding:
    receipt_input = {
        "fixture_id": fixture_id,
        "status": "hold",
        "hold_reason": reason,
        "payload_hash": payload_hash,
        "policy_version": policy["policy_version"],
    }
    return Finding(
        fixture_id=fixture_id,
        status="hold",
        hold_reason=reason,
        payload_hash=payload_hash,
        receipt_hash=sha256(receipt_input),
        policy_version=policy["policy_version"],
    )


def validate_event(event: Any, policy: dict[str, Any], fixture_id: str, operation: str = "validate") -> Finding:
    """Return allow or hold with deterministic reason; never raises for malformed fixture data."""
    payload_hash: str | None = None
    if not isinstance(event, dict):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if policy.get("reject_unknown_properties") and set(event) - EVENT_KEYS:
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if not EVENT_KEYS.issubset(event):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if event.get("schema_version") != "qafila-event.v1":
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if not nonempty_string(event.get("event_id")) or not str(event["event_id"]).startswith("evt_"):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    scalar_fields = ("created_at", "source_ref", "actor_ref", "correlation_id", "idempotency_key")
    if not all(nonempty_string(event.get(field)) for field in scalar_fields):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if event.get("content_type") not in ALLOWED_CONTENT_TYPES:
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if event.get("classification") not in ALLOWED_CLASSIFICATIONS or event.get("status") not in ALLOWED_STATUSES:
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if operation not in policy["operations"]["allowed"]:
        return hold(policy, fixture_id, "operation_denied", payload_hash)
    if event["source_ref"] not in policy["allowed_sources"]:
        return hold(policy, fixture_id, "source_not_allowed", payload_hash)

    payload = event.get("payload")
    if not isinstance(payload, dict) or set(payload) - PAYLOAD_KEYS or not {"text", "payload_hash"}.issubset(payload):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    if not nonempty_string(payload.get("text")) or not is_sha256(payload.get("payload_hash")):
        return hold(policy, fixture_id, "schema_invalid", payload_hash)
    payload_hash = payload["payload_hash"]
    canonical_payload = {key: payload.get(key) for key in sorted(PAYLOAD_KEYS - {"payload_hash"})}
    expected_payload_hash = sha256(canonical_payload)
    if policy.get("require_recomputed_payload_hash") and payload_hash != expected_payload_hash:
        return hold(policy, fixture_id, "payload_hash_mismatch", payload_hash)

    provenance = event.get("provenance")
    required_provenance = policy["required_provenance_fields"]
    if not isinstance(provenance, dict) or set(provenance) - PROVENANCE_KEYS:
        return hold(policy, fixture_id, "provenance_missing", payload_hash)
    if not all(nonempty_string(provenance.get(field)) for field in required_provenance):
        return hold(policy, fixture_id, "provenance_missing", payload_hash)
    if provenance.get("extraction_method") not in ALLOWED_EXTRACTION_METHODS or not is_sha256(provenance.get("source_hash")):
        return hold(policy, fixture_id, "provenance_missing", payload_hash)

    expected_idempotency = sha256({
        "event_id": event["event_id"],
        "source_ref": event["source_ref"],
        "payload_hash": payload_hash,
    })
    if policy.get("require_recomputed_idempotency_key") and event["idempotency_key"] != expected_idempotency:
        return hold(policy, fixture_id, "idempotency_key_mismatch", payload_hash)

    receipt_input = {
        "fixture_id": fixture_id,
        "status": "allow",
        "payload_hash": payload_hash,
        "policy_version": policy["policy_version"],
        "source_ref": event["source_ref"],
        "schema_version": event["schema_version"],
    }
    return Finding(
        fixture_id=fixture_id,
        status="allow",
        hold_reason=None,
        payload_hash=payload_hash,
        receipt_hash=sha256(receipt_input),
        policy_version=policy["policy_version"],
    )


def iter_fixtures(paths: Iterable[Path]) -> Iterable[tuple[str, dict[str, Any], str]]:
    for path in sorted(paths):
        source = load_json(path)
        yield path.stem, source.get("event", source), source.get("operation", "validate")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_benchmark(path: Path, experiment_id: str, findings: list[Finding], run_label: str) -> None:
    fields = [
        "experiment_id", "run_label", "fixture_id", "policy_version", "status",
        "hold_reason", "payload_hash", "receipt_hash", "network_egress",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for finding in findings:
            writer.writerow({
                "experiment_id": experiment_id,
                "run_label": run_label,
                "fixture_id": finding.fixture_id,
                "policy_version": finding.policy_version,
                "status": finding.status,
                "hold_reason": finding.hold_reason or "",
                "payload_hash": finding.payload_hash or "",
                "receipt_hash": finding.receipt_hash,
                "network_egress": "deny",
            })

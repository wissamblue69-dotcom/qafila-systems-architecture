from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POSITIVE = ROOT / "fixtures" / "positive"
NEGATIVE = ROOT / "fixtures" / "negative"


def canonical_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def base_event() -> dict:
    payload = {
        "text": "Qafila deterministic gate fixture for a provenance-bound evidence event.",
        "original_term": "قافلة",
        "normalized_label": "qafila-evidence",
        "relations": ["implements:governance-policy.v1"],
    }
    payload["payload_hash"] = canonical_hash(payload)
    return {
        "event_id": "evt_qafila_fixture_0001",
        "schema_version": "qafila-event.v1",
        "created_at": "2026-08-22T00:00:00Z",
        "source_ref": "fixture:qafila",
        "actor_ref": "agent:fixture-generator",
        "correlation_id": "run_qafila_poc_0001",
        "idempotency_key": canonical_hash({
            "event_id": "evt_qafila_fixture_0001",
            "source_ref": "fixture:qafila",
            "payload_hash": payload["payload_hash"],
        }),
        "content_type": "source",
        "payload": payload,
        "provenance": {
            "uri": "fixture://qafila/positive/event-0001",
            "locator": "fixture:positive:1",
            "extraction_method": "fixture",
            "source_hash": canonical_hash({"fixture": "positive-event-0001"}),
            "captured_at": "2026-08-22T00:00:00Z",
        },
        "classification": "source",
        "status": "raw",
    }


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    POSITIVE.mkdir(parents=True, exist_ok=True)
    NEGATIVE.mkdir(parents=True, exist_ok=True)
    event = base_event()
    write(POSITIVE / "01_valid_event.json", {"operation": "validate", "event": event})

    cases: list[tuple[str, dict, str]] = []
    missing_source = copy.deepcopy(event); missing_source.pop("source_ref")
    cases.append(("01_missing_source_ref", missing_source, "validate"))
    missing_locator = copy.deepcopy(event); missing_locator["provenance"].pop("locator")
    cases.append(("02_missing_locator", missing_locator, "validate"))
    missing_source_hash = copy.deepcopy(event); missing_source_hash["provenance"].pop("source_hash")
    cases.append(("03_missing_source_hash", missing_source_hash, "validate"))
    source_not_allowed = copy.deepcopy(event); source_not_allowed["source_ref"] = "github:unknown/not-allowed"
    cases.append(("04_source_not_allowed", source_not_allowed, "validate"))
    bad_schema = copy.deepcopy(event); bad_schema["schema_version"] = "qafila-event.v0"
    cases.append(("05_bad_schema_version", bad_schema, "validate"))
    bad_payload = copy.deepcopy(event); bad_payload["payload"]["payload_hash"] = "sha256:" + "0" * 64
    cases.append(("06_payload_hash_mismatch", bad_payload, "validate"))
    bad_idempotency = copy.deepcopy(event); bad_idempotency["idempotency_key"] = "sha256:" + "1" * 64
    cases.append(("07_idempotency_key_mismatch", bad_idempotency, "validate"))
    denied_operation = copy.deepcopy(event)
    cases.append(("08_operation_write_denied", denied_operation, "write"))
    unknown_property = copy.deepcopy(event); unknown_property["unreviewed_extension"] = True
    cases.append(("09_unknown_property", unknown_property, "validate"))
    bad_status = copy.deepcopy(event); bad_status["status"] = "published"
    cases.append(("10_invalid_status", bad_status, "validate"))

    for name, negative_event, operation in cases:
        write(NEGATIVE / f"{name}.json", {"operation": operation, "event": negative_event})


if __name__ == "__main__":
    main()

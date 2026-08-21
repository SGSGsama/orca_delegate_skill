#!/usr/bin/env python3
"""Compact reverse-engineering worker result JSON into a synthesis checkpoint."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DROP = {
    "raw_log", "raw_logs", "raw_output", "terminal_output", "transcript",
    "conversation", "messages", "reasoning", "stdout", "stderr",
    "raw_disassembly", "raw_pseudocode", "full_trace", "binary_blob",
}
KEEP = (
    "task_id", "status", "worker_profile", "role_intent", "context_version",
    "batch", "report_path", "contract_ref", "target", "input_manifest",
    "coverage", "evidence_index", "raw_source_refs", "candidate_anomalies",
    "repro_command", "upstream_evidence", "behavior_validation",
    "artifact_id", "artifact_digest",
    "base_revision", "analysis_revision", "conclusion", "evidence",
    "local_semantics", "confidence", "alternatives", "contradictions", "accepted_names",
    "accepted_types", "accepted_offsets", "accepted_states", "schema",
    "mutations", "validation", "new_facts", "context_delta", "risks", "questions",
    "scope_deviation", "coordinator_decision_required", "summary", "next_actions",
)


def scrub(value):
    if isinstance(value, dict):
        return {key: scrub(item) for key, item in value.items() if key not in DROP}
    if isinstance(value, list):
        return [scrub(item) for item in value]
    return value


def compact(item: dict) -> dict:
    item = scrub(item)
    out = {key: item[key] for key in KEEP if key in item and item[key] not in (None, [], {}, "")}
    if "task_id" not in out:
        out["task_id"] = item.get("id", "unknown")
    if "status" not in out:
        out["status"] = "unknown"
    return out


def load(path: str):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def make_checkpoint(
    items: list[dict],
    analysis_head: str | None = None,
    context_version: str | None = None,
) -> dict:
    tasks = [compact(item) for item in items]
    counts = {"done": 0, "blocked": 0, "failed": 0, "other": 0}
    for task in tasks:
        status = str(task.get("status", "")).lower()
        if status in {"done", "succeeded", "accepted", "complete", "completed"}:
            counts["done"] += 1
        elif status == "blocked":
            counts["blocked"] += 1
        elif status in {"failed", "error", "rejected"}:
            counts["failed"] += 1
        else:
            counts["other"] += 1
    out = {"schema": "orca.reverse-checkpoint-lite/v1", "counts": counts, "tasks": tasks}
    if analysis_head:
        out["analysis_head"] = analysis_head
    if context_version:
        out["context_version"] = context_version
    return out


def markdown(checkpoint: dict) -> str:
    counts = checkpoint["counts"]
    lines = [
        "# Reverse-Engineering Checkpoint",
        "",
        f"Done: {counts['done']} | Blocked: {counts['blocked']} | Failed: {counts['failed']} | Other: {counts['other']}",
    ]
    if checkpoint.get("analysis_head"):
        lines.append(f"Analysis head: `{checkpoint['analysis_head']}`")
    if checkpoint.get("context_version"):
        lines.append(f"Context version: `{checkpoint['context_version']}`")
    for task in checkpoint["tasks"]:
        lines += ["", f"## {task.get('task_id')} — {task.get('status')}"]
        for key in KEEP:
            if key in {"task_id", "status"} or key not in task:
                continue
            value = task[key]
            rendered = json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
            lines.append(f"- **{key}**: {rendered}")
    return "\n".join(lines) + "\n"


def self_test() -> int:
    raw = {
        "task_id": "T1",
        "status": "done",
        "role_intent": "local-semantics",
        "report_path": "reports/t1.json",
        "contract_ref": "contracts/receive-v2",
        "behavior_validation": "passed",
        "evidence_index": "reports/session-a-index.json",
        "artifact_digest": "sha256:abc",
        "conclusion": "handler parses frame header",
        "evidence": [{"function": "0x401000", "fact": "reads length"}],
        "confidence": "high",
        "raw_disassembly": "x" * 1000,
        "summary": "frame header recovered",
    }
    checkpoint = make_checkpoint([raw], "db-r7", "ctx-3")
    blob = json.dumps(checkpoint)
    assert "raw_disassembly" not in blob and "xxxxxxxx" not in blob
    assert checkpoint["counts"]["done"] == 1
    assert checkpoint["analysis_head"] == "db-r7"
    assert checkpoint["context_version"] == "ctx-3"
    assert checkpoint["tasks"][0]["role_intent"] == "local-semantics"
    assert checkpoint["tasks"][0]["evidence_index"] == "reports/session-a-index.json"
    assert checkpoint["tasks"][0]["report_path"] == "reports/t1.json"
    assert checkpoint["tasks"][0]["behavior_validation"] == "passed"
    print("self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--analysis-head")
    parser.add_argument("--context-version")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.paths:
        parser.error("at least one input JSON path is required")
    try:
        items = []
        for path in args.paths:
            items.extend(load(path))
        checkpoint = make_checkpoint(items, args.analysis_head, args.context_version)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "markdown":
        sys.stdout.write(markdown(checkpoint))
    else:
        print(json.dumps(checkpoint, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

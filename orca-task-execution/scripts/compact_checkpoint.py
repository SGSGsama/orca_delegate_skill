#!/usr/bin/env python3
"""Compact mixed Orca worker result JSON into a high-signal checkpoint."""
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
    "task_id", "status", "domain", "role", "derived_profile", "lane", "target",
    "context_version", "artifact_id", "artifact_digest", "analysis_revision",
    "batch", "input_manifest", "coverage", "report_path", "contract_ref",
    "leaf_artifacts", "evidence_index", "raw_source_refs", "candidate_anomalies",
    "conclusion", "evidence", "confidence", "alternatives", "contradictions",
    "base_commit", "head_commit", "changed_files", "mutations",
    "acceptance", "behavior_validation", "tests", "checks", "validation",
    "decisions", "new_facts", "context_delta", "risks", "questions",
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
    out.setdefault("task_id", item.get("id", "unknown"))
    out.setdefault("status", "unknown")
    return out


def load(path: str):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def make_checkpoint(
    items: list[dict],
    run_domain: str | None = None,
    integration_head: str | None = None,
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
    out = {
        "schema": "orca.task-execution-checkpoint/v1",
        "execution_owner_skill": "orca-task-execution",
        "counts": counts,
        "tasks": tasks,
    }
    for key, value in (
        ("run_domain", run_domain),
        ("integration_head", integration_head),
        ("analysis_head", analysis_head),
        ("context_version", context_version),
    ):
        if value:
            out[key] = value
    return out


def markdown(checkpoint: dict) -> str:
    counts = checkpoint["counts"]
    lines = [
        "# Orca Task Checkpoint",
        "",
        f"Done: {counts['done']} | Blocked: {counts['blocked']} | Failed: {counts['failed']} | Other: {counts['other']}",
    ]
    for key in ("run_domain", "integration_head", "analysis_head", "context_version"):
        if checkpoint.get(key):
            lines.append(f"{key}: `{checkpoint[key]}`")
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
    items = [
        {"task_id": "R1", "status": "done", "domain": "reverse", "role": "luna", "coverage": {"processed": 65}, "evidence_index": "reports/index.json", "raw_log": "x" * 1000, "summary": "indexed"},
        {"task_id": "S1", "status": "done", "domain": "software", "role": "terra", "changed_files": ["src/a.py"], "tests": ["pytest: pass"], "terminal_output": "y" * 1000, "summary": "fixed"},
    ]
    checkpoint = make_checkpoint(items, "mixed", "abc", "db-r7", "ctx-3")
    blob = json.dumps(checkpoint)
    assert "raw_log" not in blob and "terminal_output" not in blob
    assert checkpoint["counts"]["done"] == 2
    assert checkpoint["execution_owner_skill"] == "orca-task-execution"
    assert checkpoint["run_domain"] == "mixed"
    assert checkpoint["tasks"][0]["evidence_index"] == "reports/index.json"
    assert checkpoint["tasks"][1]["changed_files"] == ["src/a.py"]
    print("self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*")
    parser.add_argument("--run-domain", choices=("software", "reverse", "mixed"))
    parser.add_argument("--integration-head")
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
        checkpoint = make_checkpoint(
            items,
            args.run_domain,
            args.integration_head,
            args.analysis_head,
            args.context_version,
        )
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

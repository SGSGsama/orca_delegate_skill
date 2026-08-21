#!/usr/bin/env python3
"""Compact normalized worker result JSON into a high-signal review checkpoint."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DROP = {
    "raw_log", "raw_logs", "raw_output", "terminal_output", "transcript",
    "conversation", "messages", "reasoning", "stdout", "stderr",
}
KEEP = (
    "task_id", "status", "lane", "context_version", "batch", "report_path",
    "contract_ref", "leaf_artifacts", "behavior_validation",
    "base_commit", "head_commit", "changed_files",
    "acceptance", "tests", "checks", "decisions", "new_facts", "risks",
    "context_delta", "questions", "scope_deviation",
    "coordinator_decision_required", "summary", "next_actions",
)


def scrub(value):
    if isinstance(value, dict):
        return {k: scrub(v) for k, v in value.items() if k not in DROP}
    if isinstance(value, list):
        return [scrub(v) for v in value]
    return value


def compact(item: dict) -> dict:
    item = scrub(item)
    out = {k: item[k] for k in KEEP if k in item and item[k] not in (None, [], {}, "")}
    if "task_id" not in out:
        out["task_id"] = item.get("id", "unknown")
    if "status" not in out:
        out["status"] = "unknown"
    return out


def load(path: str):
    text = sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
    data = json.loads(text)
    return data if isinstance(data, list) else [data]


def make_checkpoint(items: list[dict], integration_head: str | None = None) -> dict:
    tasks = [compact(x) for x in items]
    counts = {"done": 0, "blocked": 0, "failed": 0, "other": 0}
    for t in tasks:
        s = str(t.get("status", "")).lower()
        if s in {"done", "succeeded", "accepted", "complete", "completed"}:
            counts["done"] += 1
        elif s == "blocked":
            counts["blocked"] += 1
        elif s in {"failed", "error", "rejected"}:
            counts["failed"] += 1
        else:
            counts["other"] += 1
    out = {"schema": "orca.dev-checkpoint-lite/v1", "counts": counts, "tasks": tasks}
    if integration_head:
        out["integration_head"] = integration_head
    return out


def markdown(cp: dict) -> str:
    c = cp["counts"]
    lines = ["# Development Checkpoint", "", f"Done: {c['done']} | Blocked: {c['blocked']} | Failed: {c['failed']} | Other: {c['other']}"]
    if cp.get("integration_head"):
        lines += [f"Integration head: `{cp['integration_head']}`"]
    for t in cp["tasks"]:
        lines += ["", f"## {t.get('task_id')} — {t.get('status')}"]
        for k in KEEP:
            if k in {"task_id", "status"} or k not in t:
                continue
            v = t[k]
            rendered = json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else str(v)
            lines.append(f"- **{k}**: {rendered}")
    return "\n".join(lines) + "\n"


def self_test() -> int:
    raw = {"task_id": "T1", "status": "done", "lane": "auth-flow", "report_path": "reports/t1.json", "contract_ref": "contracts/auth-v2", "behavior_validation": "passed", "head_commit": "abc", "tests": [{"ok": True}], "raw_log": "x" * 1000, "summary": "ok"}
    cp = make_checkpoint([raw])
    blob = json.dumps(cp)
    assert "raw_log" not in blob and "xxxxxxxx" not in blob
    assert cp["counts"]["done"] == 1
    assert cp["tasks"][0]["lane"] == "auth-flow"
    assert cp["tasks"][0]["report_path"] == "reports/t1.json"
    assert cp["tasks"][0]["behavior_validation"] == "passed"
    print("self-test: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--integration-head")
    ap.add_argument("--format", choices=("json", "markdown"), default="json")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.paths:
        ap.error("at least one input JSON path is required")
    try:
        items = []
        for p in args.paths:
            items.extend(load(p))
        cp = make_checkpoint(items, args.integration_head)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "markdown":
        sys.stdout.write(markdown(cp))
    else:
        print(json.dumps(cp, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

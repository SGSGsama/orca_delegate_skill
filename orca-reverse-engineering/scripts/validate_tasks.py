#!/usr/bin/env python3
"""Lightweight TaskGraphLite validator for orca-reverse-engineering."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import PurePosixPath

ROLES = {"terra-max", "luna-max", "coordinator", "read-only"}
RISKS = {"low", "medium", "high"}
GLOB_CHARS = "*?["


def norm_scope(value: str) -> str:
    return value.replace("\\", "/").strip()


def scope_problem(value: str) -> str | None:
    scope = norm_scope(value)
    if not scope:
        return "empty scope"
    if scope.startswith("/") or (len(scope) > 2 and scope[1:3] == ":/"):
        return "absolute scope; use a relative logical artifact identifier"
    if ".." in PurePosixPath(scope).parts:
        return "parent traversal"
    if scope in {"*", "**", "**/*", "."}:
        return "over-broad scope"
    return None


def static_prefix(value: str) -> str:
    """Return the literal prefix before the first glob metacharacter."""
    value = norm_scope(value)
    indexes = [value.find(ch) for ch in GLOB_CHARS if ch in value]
    return value[:min(indexes)] if indexes else value


def overlaps(a: str, b: str) -> bool:
    a, b = norm_scope(a), norm_scope(b)
    if a == b:
        return True
    a_glob = any(ch in a for ch in GLOB_CHARS)
    b_glob = any(ch in b for ch in GLOB_CHARS)
    if a_glob and fnmatch.fnmatch(b, a):
        return True
    if b_glob and fnmatch.fnmatch(a, b):
        return True
    # Two patterns may intersect even when neither literal pattern string
    # matches the other. If their static prefixes are not provably disjoint,
    # report a possible conflict rather than a false safe result.
    if a_glob and b_glob:
        ap, bp = static_prefix(a), static_prefix(b)
        return not ap or not bp or ap.startswith(bp) or bp.startswith(ap)
    aa, bb = a.rstrip("/"), b.rstrip("/")
    return aa.startswith(bb + "/") or bb.startswith(aa + "/")


def transitive_dep(tasks: dict[str, dict], src: str, target: str, seen=None) -> bool:
    if src == target:
        return True
    seen = set() if seen is None else seen
    if src in seen or src not in tasks:
        return False
    seen.add(src)
    return any(transitive_dep(tasks, dep, target, seen) for dep in tasks[src].get("depends_on", []))


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["top-level input must be an object"], []
    raw = data.get("tasks")
    if not isinstance(raw, list) or not raw:
        return ["top-level 'tasks' must be a non-empty list"], []

    tasks: dict[str, dict] = {}
    for index, task in enumerate(raw):
        if not isinstance(task, dict):
            errors.append(f"tasks[{index}] must be an object")
            continue
        task_id = task.get("id")
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f"tasks[{index}].id must be a non-empty string")
            continue
        if task_id in tasks:
            errors.append(f"duplicate task id: {task_id}")
            continue
        tasks[task_id] = dict(task)

    for task_id, task in tasks.items():
        role = task.get("role")
        if not isinstance(role, str) or role not in ROLES:
            errors.append(f"{task_id}: invalid role {role!r}")
        risk = task.get("risk", "low")
        if not isinstance(risk, str) or risk not in RISKS:
            errors.append(f"{task_id}: invalid risk {risk!r}")

        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(item, str) for item in deps):
            errors.append(f"{task_id}: depends_on must be a string list")
            deps = []
        task["depends_on"] = deps
        for dep in deps:
            if dep not in tasks:
                errors.append(f"{task_id}: missing dependency {dep}")
            elif dep == task_id:
                errors.append(f"{task_id}: self dependency")

        for field in ("read", "mutate"):
            scopes = task.get(field, [])
            if not isinstance(scopes, list) or not all(isinstance(item, str) for item in scopes):
                errors.append(f"{task_id}: {field} must be a string list")
                scopes = []
            task[field] = [norm_scope(scope) for scope in scopes]
            for scope in scopes:
                if problem := scope_problem(scope):
                    errors.append(f"{task_id}: {field} scope {scope!r}: {problem}")

        if role == "luna-max" and risk == "high":
            warnings.append(f"{task_id}: high-risk interpretation routed to Luna Max")
        if role in {"coordinator", "read-only"} and task.get("mutate"):
            warnings.append(f"{task_id}: {role} task has mutation scope")

    visiting: set[str] = set()
    visited: set[str] = set()

    def dfs(task_id: str, stack: list[str]) -> None:
        if task_id in visiting:
            errors.append("dependency cycle: " + " -> ".join(stack + [task_id]))
            return
        if task_id in visited or task_id not in tasks:
            return
        visiting.add(task_id)
        for dep in tasks[task_id].get("depends_on", []):
            dfs(dep, stack + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        dfs(task_id, [])

    task_ids = list(tasks)
    for index, left_id in enumerate(task_ids):
        for right_id in task_ids[index + 1:]:
            if transitive_dep(tasks, left_id, right_id) or transitive_dep(tasks, right_id, left_id):
                continue
            left, right = tasks[left_id], tasks[right_id]
            left_mutate, right_mutate = left.get("mutate", []), right.get("mutate", [])
            left_read, right_read = left.get("read", []), right.get("read", [])
            for left_scope in left_mutate:
                for right_scope in right_mutate:
                    if overlaps(left_scope, right_scope):
                        errors.append(
                            f"parallel mutation overlap: {left_id}:{left_scope} <-> {right_id}:{right_scope}"
                        )
            for left_scope in left_mutate:
                for right_scope in right_read:
                    if overlaps(left_scope, right_scope):
                        warnings.append(
                            f"parallel mutation/read hazard: {left_id}:{left_scope} -> {right_id}:{right_scope}"
                        )
            for right_scope in right_mutate:
                for left_scope in left_read:
                    if overlaps(right_scope, left_scope):
                        warnings.append(
                            f"parallel mutation/read hazard: {right_id}:{right_scope} -> {left_id}:{left_scope}"
                        )

    return sorted(set(errors)), sorted(set(warnings))


def self_test() -> int:
    good = {"tasks": [
        {"id": "T1", "role": "terra-max", "depends_on": [], "read": ["binary/main/functions/receive/**"], "mutate": [], "risk": "medium"},
        {"id": "T2", "role": "luna-max", "depends_on": ["T1"], "read": ["analysis/main.bndb/functions/receive/**"], "mutate": ["analysis/main.bndb/names/receive/**"], "risk": "low"},
    ]}
    overlap = {"tasks": [
        {"id": "A", "role": "luna-max", "depends_on": [], "read": [], "mutate": ["analysis/main.bndb/names/receive/*.fn"], "risk": "low"},
        {"id": "B", "role": "terra-max", "depends_on": [], "read": [], "mutate": ["analysis/main.bndb/**/receive.fn"], "risk": "medium"},
    ]}
    disjoint = {"tasks": [
        {"id": "D1", "role": "luna-max", "depends_on": [], "read": [], "mutate": ["analysis/a.bndb/names/**"], "risk": "low"},
        {"id": "D2", "role": "luna-max", "depends_on": [], "read": [], "mutate": ["reports/b.md/sections/**"], "risk": "low"},
    ]}
    malformed = {"tasks": [
        {"id": "M1", "role": "terra-max", "depends_on": None, "read": None, "mutate": None, "risk": "medium"},
    ]}

    good_errors, _ = validate(good)
    overlap_errors, _ = validate(overlap)
    disjoint_errors, _ = validate(disjoint)
    malformed_errors, _ = validate(malformed)
    assert not good_errors, good_errors
    assert any("parallel mutation overlap" in item for item in overlap_errors), overlap_errors
    assert not disjoint_errors, disjoint_errors
    assert any("depends_on must be a string list" in item for item in malformed_errors), malformed_errors
    assert any("read must be a string list" in item for item in malformed_errors), malformed_errors
    assert any("mutate must be a string list" in item for item in malformed_errors), malformed_errors
    print("self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", help="TaskGraphLite JSON path, or - for stdin")
    parser.add_argument("--strict", action="store_true", help="treat warnings as failure")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.path:
        parser.error("path is required unless --self-test is used")
    try:
        text = sys.stdin.read() if args.path == "-" else open(args.path, encoding="utf-8").read()
        data = json.loads(text)
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [f"input error: {exc}"], "warnings": []}, ensure_ascii=False, indent=2))
        return 2
    errors, warnings = validate(data)
    ok = not errors and not (args.strict and warnings)
    print(json.dumps({"ok": ok, "errors": errors, "warnings": warnings, "strict": args.strict}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

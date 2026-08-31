#!/usr/bin/env python3
"""Validate a compact orca-task-execution TaskGraphLite document."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import PurePosixPath

OWNER = "orca-task-execution"
RUN_DOMAINS = {"software", "reverse", "mixed"}
TASK_DOMAINS = {"software", "reverse"}
ROLES = {"terra", "luna"}
RISKS = {"low", "medium", "high"}
GLOB_CHARS = "*?["


def norm_scope(value: str) -> str:
    return value.replace("\\", "/").strip()


def scope_problem(value: str) -> str | None:
    scope = norm_scope(value)
    if not scope:
        return "empty scope"
    if scope.startswith("/") or (len(scope) > 2 and scope[1:3] == ":/"):
        return "absolute scope; use a relative logical identifier"
    if ".." in PurePosixPath(scope).parts:
        return "parent traversal"
    if scope in {"*", "**", "**/*", "."}:
        return "over-broad scope"
    return None


def static_prefix(value: str) -> str:
    value = norm_scope(value)
    indexes = [value.find(char) for char in GLOB_CHARS if char in value]
    return value[: min(indexes)] if indexes else value


def overlaps(left: str, right: str) -> bool:
    left, right = norm_scope(left), norm_scope(right)
    if left == right:
        return True
    left_glob = any(char in left for char in GLOB_CHARS)
    right_glob = any(char in right for char in GLOB_CHARS)
    if left_glob and fnmatch.fnmatch(right, left):
        return True
    if right_glob and fnmatch.fnmatch(left, right):
        return True
    if left_glob and right_glob:
        lp, rp = static_prefix(left), static_prefix(right)
        return not lp or not rp or lp.startswith(rp) or rp.startswith(lp)
    ll, rr = left.rstrip("/"), right.rstrip("/")
    return ll.startswith(rr + "/") or rr.startswith(ll + "/")


def transitive_dep(tasks: dict[str, dict], source: str, target: str, seen=None) -> bool:
    if source == target:
        return True
    seen = set() if seen is None else seen
    if source in seen or source not in tasks:
        return False
    seen.add(source)
    return any(
        transitive_dep(tasks, dep, target, seen)
        for dep in tasks[source].get("depends_on", [])
    )


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return ["top-level input must be an object"], []
    if data.get("execution_owner_skill") != OWNER:
        errors.append(f"execution_owner_skill must be {OWNER!r}")
    run_domain = data.get("run_domain")
    if run_domain not in RUN_DOMAINS:
        errors.append(f"run_domain must be one of {sorted(RUN_DOMAINS)!r}")

    raw = data.get("tasks")
    if not isinstance(raw, list) or not raw:
        errors.append("top-level 'tasks' must be a non-empty list")
        return sorted(set(errors)), warnings

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
        domain = task.get("domain")
        role = task.get("role")
        risk = task.get("risk", "low")
        if domain not in TASK_DOMAINS:
            errors.append(f"{task_id}: domain must be software or reverse, got {domain!r}")
        elif run_domain in TASK_DOMAINS and domain != run_domain:
            errors.append(f"{task_id}: domain {domain!r} conflicts with Run domain {run_domain!r}")
        if role not in ROLES:
            errors.append(f"{task_id}: role must be terra or luna, got {role!r}")
        if "profile" in task or "model" in task or "effort" in task:
            errors.append(f"{task_id}: profile/model/effort must be derived from domain and role")
        if risk not in RISKS:
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

        for field in ("read", "write"):
            scopes = task.get(field, [])
            if not isinstance(scopes, list) or not all(isinstance(item, str) for item in scopes):
                errors.append(f"{task_id}: {field} must be a string list")
                scopes = []
            task[field] = [norm_scope(scope) for scope in scopes]
            for scope in scopes:
                if problem := scope_problem(scope):
                    errors.append(f"{task_id}: {field} scope {scope!r}: {problem}")

        if role == "luna" and risk == "high":
            warnings.append(f"{task_id}: high-risk work routed to Luna")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str, stack: list[str]) -> None:
        if task_id in visiting:
            errors.append("dependency cycle: " + " -> ".join(stack + [task_id]))
            return
        if task_id in visited or task_id not in tasks:
            return
        visiting.add(task_id)
        for dep in tasks[task_id].get("depends_on", []):
            visit(dep, stack + [task_id])
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id, [])

    ids = list(tasks)
    for index, left_id in enumerate(ids):
        for right_id in ids[index + 1 :]:
            if transitive_dep(tasks, left_id, right_id) or transitive_dep(tasks, right_id, left_id):
                continue
            left, right = tasks[left_id], tasks[right_id]
            for left_scope in left.get("write", []):
                for right_scope in right.get("write", []):
                    if overlaps(left_scope, right_scope):
                        errors.append(
                            f"parallel write overlap: {left_id}:{left_scope} <-> {right_id}:{right_scope}"
                        )
                for right_scope in right.get("read", []):
                    if overlaps(left_scope, right_scope):
                        warnings.append(
                            f"parallel write/read hazard: {left_id}:{left_scope} -> {right_id}:{right_scope}"
                        )
            for right_scope in right.get("write", []):
                for left_scope in left.get("read", []):
                    if overlaps(right_scope, left_scope):
                        warnings.append(
                            f"parallel write/read hazard: {right_id}:{right_scope} -> {left_id}:{left_scope}"
                        )

    return sorted(set(errors)), sorted(set(warnings))


def self_test() -> int:
    good = {
        "execution_owner_skill": OWNER,
        "run_domain": "mixed",
        "tasks": [
            {"id": "R1", "domain": "reverse", "role": "luna", "depends_on": [], "read": ["traces/a/**"], "write": ["reports/a/**"], "risk": "low"},
            {"id": "S1", "domain": "software", "role": "terra", "depends_on": ["R1"], "read": ["reports/a/**", "src/a.py"], "write": ["src/a.py"], "risk": "medium"},
        ],
    }
    overlap = {
        "execution_owner_skill": OWNER,
        "run_domain": "software",
        "tasks": [
            {"id": "A", "domain": "software", "role": "luna", "depends_on": [], "read": [], "write": ["src/auth/*.py"], "risk": "low"},
            {"id": "B", "domain": "software", "role": "terra", "depends_on": [], "read": [], "write": ["src/**/service.py"], "risk": "medium"},
        ],
    }
    foreign = {**good, "execution_owner_skill": "bn"}
    mixed_task = {
        "execution_owner_skill": OWNER,
        "run_domain": "mixed",
        "tasks": [{"id": "M", "domain": "mixed", "role": "terra", "depends_on": [], "read": [], "write": [], "risk": "low"}],
    }
    explicit_profile = {
        "execution_owner_skill": OWNER,
        "run_domain": "reverse",
        "tasks": [{"id": "P", "domain": "reverse", "role": "terra", "profile": "custom", "depends_on": [], "read": [], "write": [], "risk": "low"}],
    }

    good_errors, _ = validate(good)
    overlap_errors, _ = validate(overlap)
    foreign_errors, _ = validate(foreign)
    mixed_errors, _ = validate(mixed_task)
    profile_errors, _ = validate(explicit_profile)
    assert not good_errors, good_errors
    assert any("parallel write overlap" in item for item in overlap_errors), overlap_errors
    assert any("execution_owner_skill" in item for item in foreign_errors), foreign_errors
    assert any("domain must be software or reverse" in item for item in mixed_errors), mixed_errors
    assert any("must be derived" in item for item in profile_errors), profile_errors
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

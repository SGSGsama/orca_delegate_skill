#!/usr/bin/env python3
"""Lightweight TaskGraphLite validator for orca-software-development."""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import PurePosixPath

ROLES = {"luna-max", "terra-xhigh", "coordinator", "read-only"}
RISKS = {"low", "medium", "high"}
GLOB_CHARS = "*?["


def norm_path(value: str) -> str:
    return value.replace("\\", "/").strip()


def path_problem(value: str) -> str | None:
    p = norm_path(value)
    if not p:
        return "empty path"
    if p.startswith("/") or (len(p) > 2 and p[1:3] == ":/"):
        return "absolute path"
    if ".." in PurePosixPath(p).parts:
        return "parent traversal"
    if p in {"*", "**", "**/*", "."}:
        return "over-broad scope"
    return None


def static_prefix(value: str) -> str:
    """Return the literal prefix before the first glob metacharacter."""
    value = norm_path(value)
    indexes = [value.find(ch) for ch in GLOB_CHARS if ch in value]
    return value[:min(indexes)] if indexes else value


def overlaps(a: str, b: str) -> bool:
    a, b = norm_path(a), norm_path(b)
    if a == b:
        return True
    # Conservative glob handling in either direction.
    a_glob = any(ch in a for ch in GLOB_CHARS)
    b_glob = any(ch in b for ch in GLOB_CHARS)
    if a_glob and fnmatch.fnmatch(b, a):
        return True
    if b_glob and fnmatch.fnmatch(a, b):
        return True
    # Comparing two patterns as literal strings misses intersecting scopes such
    # as src/auth/*.ts and src/**/service.ts. If their literal prefixes are not
    # provably disjoint, report a possible overlap rather than a false safe result.
    if a_glob and b_glob:
        ap, bp = static_prefix(a), static_prefix(b)
        return not ap or not bp or ap.startswith(bp) or bp.startswith(ap)
    # Directory-prefix approximation for scopes such as src/auth/.
    aa, bb = a.rstrip("/"), b.rstrip("/")
    return aa.startswith(bb + "/") or bb.startswith(aa + "/")


def transitive_dep(tasks: dict[str, dict], src: str, target: str, seen=None) -> bool:
    if src == target:
        return True
    seen = set() if seen is None else seen
    if src in seen or src not in tasks:
        return False
    seen.add(src)
    return any(transitive_dep(tasks, d, target, seen) for d in tasks[src].get("depends_on", []))


def validate(data: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    raw = data.get("tasks")
    if not isinstance(raw, list) or not raw:
        return ["top-level 'tasks' must be a non-empty list"], []

    tasks: dict[str, dict] = {}
    for i, task in enumerate(raw):
        if not isinstance(task, dict):
            errors.append(f"tasks[{i}] must be an object")
            continue
        tid = task.get("id")
        if not isinstance(tid, str) or not tid.strip():
            errors.append(f"tasks[{i}].id must be a non-empty string")
            continue
        if tid in tasks:
            errors.append(f"duplicate task id: {tid}")
            continue
        tasks[tid] = dict(task)

    for tid, task in tasks.items():
        role = task.get("role")
        if not isinstance(role, str) or role not in ROLES:
            errors.append(f"{tid}: invalid role {role!r}")
        risk = task.get("risk", "low")
        if not isinstance(risk, str) or risk not in RISKS:
            errors.append(f"{tid}: invalid risk {risk!r}")
        deps = task.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
            errors.append(f"{tid}: depends_on must be a string list")
            deps = []
        task["depends_on"] = deps
        for dep in deps:
            if dep not in tasks:
                errors.append(f"{tid}: missing dependency {dep}")
            elif dep == tid:
                errors.append(f"{tid}: self dependency")
        for field in ("read", "write"):
            paths = task.get(field, [])
            if not isinstance(paths, list) or not all(isinstance(x, str) for x in paths):
                errors.append(f"{tid}: {field} must be a string list")
                paths = []
            task[field] = [norm_path(p) for p in paths]
            for p in paths:
                if problem := path_problem(p):
                    errors.append(f"{tid}: {field} scope {p!r}: {problem}")
        if role == "luna-max" and risk == "high":
            warnings.append(f"{tid}: high-risk work routed to Luna Max")
        if role == "coordinator" and task.get("write"):
            warnings.append(f"{tid}: coordinator task has writable implementation scope")

    # Detect cycles after dependency existence checks.
    visiting, visited = set(), set()
    def dfs(tid: str, stack: list[str]):
        if tid in visiting:
            errors.append("dependency cycle: " + " -> ".join(stack + [tid]))
            return
        if tid in visited or tid not in tasks:
            return
        visiting.add(tid)
        for dep in tasks[tid].get("depends_on", []):
            dfs(dep, stack + [tid])
        visiting.remove(tid)
        visited.add(tid)
    for tid in tasks:
        dfs(tid, [])

    ids = list(tasks)
    for i, a_id in enumerate(ids):
        for b_id in ids[i + 1:]:
            # Ordered tasks are not parallel hazards.
            if transitive_dep(tasks, a_id, b_id) or transitive_dep(tasks, b_id, a_id):
                continue
            a, b = tasks[a_id], tasks[b_id]
            aw, bw = a.get("write", []), b.get("write", [])
            ar, br = a.get("read", []), b.get("read", [])
            for x in aw:
                for y in bw:
                    if overlaps(x, y):
                        errors.append(f"parallel write overlap: {a_id}:{x} <-> {b_id}:{y}")
            for x in aw:
                for y in br:
                    if overlaps(x, y):
                        warnings.append(f"parallel write/read hazard: {a_id}:{x} -> {b_id}:{y}")
            for x in bw:
                for y in ar:
                    if overlaps(x, y):
                        warnings.append(f"parallel write/read hazard: {b_id}:{x} -> {a_id}:{y}")

    return sorted(set(errors)), sorted(set(warnings))


def self_test() -> int:
    good = {"tasks": [
        {"id": "T1", "role": "terra-xhigh", "depends_on": [], "read": ["src/a.ts"], "write": ["src/a.ts"], "risk": "medium"},
        {"id": "T2", "role": "luna-max", "depends_on": ["T1"], "read": ["src/a.ts"], "write": ["tests/a.test.ts"], "risk": "low"},
    ]}
    bad = {"tasks": [
        {"id": "A", "role": "luna-max", "depends_on": [], "read": [], "write": ["src/**"], "risk": "low"},
        {"id": "B", "role": "terra-xhigh", "depends_on": [], "read": [], "write": ["src/x.ts"], "risk": "medium"},
    ]}
    intersecting_globs = {"tasks": [
        {"id": "G1", "role": "luna-max", "depends_on": [], "read": [], "write": ["src/auth/*.ts"], "risk": "low"},
        {"id": "G2", "role": "terra-xhigh", "depends_on": [], "read": [], "write": ["src/**/service.ts"], "risk": "medium"},
    ]}
    disjoint_globs = {"tasks": [
        {"id": "D1", "role": "luna-max", "depends_on": [], "read": [], "write": ["src/auth/*.ts"], "risk": "low"},
        {"id": "D2", "role": "terra-xhigh", "depends_on": [], "read": [], "write": ["tests/auth/*.ts"], "risk": "medium"},
    ]}
    malformed = {"tasks": [
        {"id": "M1", "role": "luna-max", "depends_on": None, "read": [], "write": None, "risk": "low"},
    ]}
    e1, _ = validate(good)
    e2, _ = validate(bad)
    e3, _ = validate(intersecting_globs)
    e4, _ = validate(disjoint_globs)
    e5, _ = validate(malformed)
    assert not e1, e1
    assert any("parallel write overlap" in x for x in e2), e2
    assert any("parallel write overlap" in x for x in e3), e3
    assert not e4, e4
    assert any("depends_on must be a string list" in x for x in e5), e5
    assert any("write must be a string list" in x for x in e5), e5
    print("self-test: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="TaskGraphLite JSON path, or - for stdin")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failure")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not args.path:
        ap.error("path is required unless --self-test is used")
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

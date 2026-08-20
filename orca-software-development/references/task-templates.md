# Software-Development Task Templates

Read only the template matching the next bounded task. Replace every angle-bracket placeholder and remove irrelevant fields before dispatch.

For implementation tasks, choose the Luna profile for a precise mechanical contract or replace it with `[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]` when substantial local reasoning remains. Keep the selected profile as the first line of the final Task spec.

`Shared context packet` must contain the accepted Run-level objective, architecture/contracts, relevant repository instructions, module map, user-owned changes, and known validation commands. Inline it unless every worker is proven to share the referenced path. `Local starting points` should name exact files, symbols, tests, or commands so the worker does not repeat repository-wide discovery.

## Implementation

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Implement <behavior>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact files, symbols, tests, and commands>.
Writable scope: <files/directories>.
Must preserve: <public APIs, compatibility, invariants>.
May change: <explicit interfaces or internals>.
Behavior and errors: <inputs, outputs, edge cases, failure modes>.
Acceptance criteria: <observable checks>.
Validation: run <exact commands>.
Do not: <out-of-scope changes, dependencies, generated files>.
Complete in this Task: local inspection, implementation, targeted tests, and ordinary repair.
Return: changed files; design choices; validation results; remaining risks.
```

## Diagnosis only

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
Objective: Find the root cause of <failure>; do not implement a fix.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact files, symbols, logs, tests, and commands>.
Scope: <components/files/tests/logs>.
Reproduction: <command and expected/actual result>.
Known evidence: <facts, not assumptions>.
Questions: first incorrect state, causal chain, affected scope, and smallest plausible fix surface.
Return: root cause with evidence; confidence; ruled-out alternatives; proposed fix and regression test.
```

## Tests only

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Add tests that demonstrate <contract/regression>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact test files, production symbols, fixtures, and commands>.
Writable scope: <test files/fixtures only>.
Production code must not change.
Cover: <normal, boundary, error, concurrency cases>.
Validation: run <exact commands>.
Return: tests added; what each proves; observed failures or passes; fixture changes.
```

## Review only

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
Objective: Review <diff/commit/files> against <requirement>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact diff, files, contracts, and validation evidence>.
Read-only: do not edit files.
Check: correctness, regressions, API/behavior compatibility, error paths, concurrency, security, and missing tests as relevant.
Return findings ordered by severity, each with file/line evidence and a concrete failure scenario. State explicitly if no findings remain and list residual validation gaps.
```

## Narrow repair

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Fix the accepted finding <finding ID/summary>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact finding evidence, files, symbols, tests, and commands>.
Writable scope: <smallest file set>.
Required behavior: <correct outcome>.
Preserve: <interfaces/invariants/unrelated behavior>.
Regression test: <specific test to add or update>.
Validation: run <exact commands>.
Complete in this Task: local confirmation, repair, regression test, and ordinary follow-up correction.
Return: root fix; changed files; regression evidence; remaining risk.
```
.

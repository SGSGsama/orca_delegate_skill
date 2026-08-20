# Software-Development Task Templates

Read only the template matching the next bounded task. Replace every angle-bracket placeholder and remove irrelevant fields before dispatch.

For implementation tasks, choose the Luna profile for a precise mechanical contract or replace it with `[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]` when substantial local reasoning remains. Keep the selected profile as the first line of the final Task spec.

## Implementation

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Implement <behavior>.
Writable scope: <files/directories>.
Must preserve: <public APIs, compatibility, invariants>.
May change: <explicit interfaces or internals>.
Behavior and errors: <inputs, outputs, edge cases, failure modes>.
Acceptance criteria: <observable checks>.
Validation: run <exact commands>.
Do not: <out-of-scope changes, dependencies, generated files>.
Return: changed files; design choices; validation results; remaining risks.
```

## Diagnosis only

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
Objective: Find the root cause of <failure>; do not implement a fix.
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
Read-only: do not edit files.
Check: correctness, regressions, API/behavior compatibility, error paths, concurrency, security, and missing tests as relevant.
Return findings ordered by severity, each with file/line evidence and a concrete failure scenario. State explicitly if no findings remain and list residual validation gaps.
```

## Narrow repair

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Fix the accepted finding <finding ID/summary>.
Writable scope: <smallest file set>.
Required behavior: <correct outcome>.
Preserve: <interfaces/invariants/unrelated behavior>.
Regression test: <specific test to add or update>.
Validation: run <exact commands>.
Return: root fix; changed files; regression evidence; remaining risk.
```
.

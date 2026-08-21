# Compact Task Contracts

Prefer short text Task specs. The primary coordinator agent should decide boundaries and contracts; Luna or a deterministic helper can materialize boilerplate.

## Worker Task

The worker profile must be the first line.

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Task: T2
Type: implementation | diagnosis | tests | review | repair
Objective: <one verifiable outcome>
Context: <Run Context ref/version + short fallback facts>
Starts: <exact files/symbols/tests/logs/commands>
Depends: <task IDs or none>
Read: <bounded paths/symbols>
Write: <bounded paths; none for read-only>
Forbidden: <interfaces/files/behaviors that must not change>
Preserve: <invariants/compatibility/error semantics>
Acceptance: <observable behaviors and exact validation commands>
Escalate: <what invalidates the contract or requires global decision>
Return: changed files/commit if applicable; validation evidence; new facts; risks; deviations.
```

Use the Terra profile instead when routing requires Terra XHigh.

## Diagnosis Task

Keep it read-only unless an experiment explicitly needs files:

```text
Objective: determine <unknown cause>
Reproduction: <command + expected/actual>
Known evidence: <facts only>
Questions: first incorrect state; causal chain; affected scope; smallest plausible fix surface
Return: root cause with evidence; confidence; ruled-out alternatives; proposed fix/test surface
```

## Review Task

```text
Objective: review <diff/commit/files> against <requirement>
Read-only: true
Evidence: <diff ref + validation/checkpoint refs>
Check: correctness; compatibility; error paths; concurrency/security when relevant; missing tests
Return: findings by severity with concrete evidence; residual validation gaps; accept/revise recommendation
```

## Same-worker repair delta

Do not resend the entire Task after an ordinary local defect:

```text
Retry-of: <Task/Dispatch/result ref>
Reason: LOCAL_IMPLEMENTATION_DEFECT
Failing acceptance: <IDs or commands>
New evidence: <minimal failure output/ref>
Scope delta: <usually none>
Required correction: <specific defect>
Return: corrected result + regression evidence
```

Escalate instead if the failure requires changing shared contracts, architecture, security/data rules, or materially expanding scope.

## Worker result

Normalize results to this compact shape before review:

```text
Task / status
Base / head commit
Changed files
Acceptance evidence
Tests/checks with result refs
Decisions made inside delegated authority
New facts
Risks / unresolved questions
Scope deviation
One-paragraph summary
```

Do not attach full transcripts, full terminal logs, or copied source files.

## TaskGraphLite sidecar

When deterministic preflight is useful, materialize only orchestration facts:

```json
{
  "tasks": [
    {
      "id": "T1",
      "role": "terra-xhigh",
      "depends_on": [],
      "read": ["src/auth/**"],
      "write": ["src/auth/service.ts"],
      "risk": "medium"
    },
    {
      "id": "T2",
      "role": "luna-max",
      "depends_on": [],
      "read": ["src/auth/contracts.ts"],
      "write": ["tests/auth/token.test.ts"],
      "risk": "low"
    }
  ]
}
```

This sidecar is for validation, not a requirement that the primary coordinator agent emit verbose JSON.

## Compact review packet

High-tier review receives only:

```text
User objective and acceptance criteria
Relevant accepted decisions/contracts
Base..integration diff reference
Compact checkpoint
Aggregate validation evidence
Material unresolved risks/questions
Requested review reason code
```

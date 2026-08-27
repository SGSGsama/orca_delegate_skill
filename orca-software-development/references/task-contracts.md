# Compact Task Contracts

Prefer short text Task specs. The primary coordinator agent should decide boundaries and contracts; Luna or a deterministic helper can materialize boilerplate.

## Closed authority envelope

A delegated Task is a closed authority envelope. `Objective` and `Acceptance` describe the desired result; they do not grant authority beyond the explicit `Lane`, `Contract`, `Read`, `Write`, `Batch`, `Evidence budget`, `Expansion allowance`, and decision role. Newly discovered transitive files, modules, logs, runs, platforms, or contract questions remain outside the Task unless the allowance names them. When completion requires broader authority, preserve completed in-scope work and return one of these requests instead of expanding independently:

```text
NEED_SCOPE: exact additional files/symbols/write surface and why they are required
NEED_BULK_EVIDENCE: exact query, fields, input manifest, coverage, and raw-reference format for Luna
NEED_CONTRACT_DECISION: evidence and the shared API/schema/behavior/security/data decision required
```

Only the primary coordinator may approve a scope delta or contract decision. Reusing a warm worker or terminal preserves context, not authority.

## Worker Task

The worker profile must be the first line.

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Task: T2
Type: composition | implementation | diagnosis | tests | review | repair
Objective: <one verifiable outcome>
Context: <Run Context ref/version + short fallback facts>
Lane: <stable semantic lane ID; current Terra composer/terminal when continuing>
Contract: <accepted Task/product inputs, outputs, invariants, and behavior oracle>
Starts: <exact files/symbols/tests/logs/commands>
Batch: <bounded item set or manifest; none for a cohesive Terra lane>
Leaf artifacts: <accepted Luna result refs to compose; none>
Depends: <task IDs or none>
Read: <bounded paths/symbols>
Write: <bounded paths; none for read-only>
Forbidden: <interfaces/files/behaviors that must not change>
Scope mode: closed
Expansion allowance: <none or exact named adjacent files/symbols/log ranges>
Decision authority: <cohesive lane semantics or frozen-contract leaf work>
Evidence budget: <named logs/ranges/runs; additional raw sources none by default>
Preserve: <invariants/compatibility/error semantics>
Acceptance: <observable behaviors and exact validation commands>
Escalate: <what invalidates the contract or requires global decision>
Return: normalized result/report path; changed files/commit if applicable; composed leaf artifacts; contract/behavior validation evidence; context delta; risks; deviations; scope request if any.
```

Use the Terra profile instead when routing requires Terra XHigh.

## Worker role boundaries

### Terra composer

Terra owns semantic reasoning inside the coordinator-approved lane: causal diagnosis, cohesive implementation, integration, tests, and ordinary repair. It may inspect Task-named raw logs and the explicitly allowed adjacent context needed to reconstruct one causal chain. It must not turn that inspection into corpus-wide enumeration, repeated-run/platform comparison, or schema-driven bulk extraction. When more logs, runs, platforms, captures, or repetitive evidence are required, return `NEED_BULK_EVIDENCE`; when the lane or contract must materially expand, return `NEED_SCOPE` or `NEED_CONTRACT_DECISION`.

### Luna leaf worker

Luna owns bounded work under frozen inputs, interfaces, schemas, and acceptance criteria. It may process the complete explicit batch or evidence manifest, but must not invent semantics, change the accepted contract, or widen read/write scope to make contradictory items fit. Record and skip contradictory items when safe, continue independent items, and return one grouped `NEED_CONTRACT_DECISION` when the frozen contract is invalid.

## Diagnosis Task

Keep it read-only unless an experiment explicitly needs files:

```text
Objective: determine <unknown cause>
Reproduction: <command + expected/actual>
Known evidence: <facts only>
Questions: first incorrect state; causal chain; affected scope; smallest plausible fix surface
Evidence mode: causal-inspection
Evidence budget: <named logs/ranges/runs; broad corpus processing forbidden for Terra>
Return: root cause with evidence; confidence; ruled-out alternatives; proposed fix/test surface; bulk-evidence request if needed
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
Lane: <same lane and worker unless replacement is justified>
Failing acceptance: <IDs or commands>
New evidence: <minimal failure output/ref>
Scope delta: <usually none>
Required correction: <specific defect>
Return: corrected result + regression evidence
```

`Scope delta` is coordinator-issued; `none` grants no expansion. Escalate instead if the failure requires changing shared contracts, architecture, security/data rules, or materially expanding scope.

## Worker result

Normalize results to this compact shape before review:

```text
Task / status
Lane / context version
Contract reference
Leaf artifacts composed
Base / head commit
Changed files
Acceptance evidence
Behavior validation
Tests/checks with result refs
Decisions made inside delegated authority
Actual files/log ranges/evidence manifests inspected
New facts
Context delta
Risks / unresolved questions
Scope deviation
Scope/bulk-evidence/contract-decision request, or none
Report path
Coordinator decision required, or none
One-paragraph summary
```

Write this result to a durable report when the Task is non-trivial. The lifecycle `worker_done` body is at most three short sentences containing status, acceptance/blocker, and report path. Do not attach full transcripts, full terminal logs, or copied source files.

## TaskGraphLite sidecar

When deterministic preflight is useful, materialize only orchestration facts:

```json
{
  "tasks": [
    {
      "id": "T1",
      "role": "terra-xhigh",
      "context_lane": "auth-flow",
      "depends_on": [],
      "read": ["src/auth/**"],
      "write": ["src/auth/service.ts"],
      "risk": "medium"
    },
    {
      "id": "T2",
      "role": "luna-max",
      "context_lane": "auth-contract-batch",
      "batch": "token-fixtures",
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

## Primary coordinator output envelopes

Default primary-coordinator output is sparse and decision-shaped. Expand it when user needs, safety, uncertainty, or the decision itself requires more context; avoid narrating lifecycle receipts or restating worker reports without a reason.

```text
INITIAL
Shape: direct | single-terra-composer | multi-agent
TaskGraph/context refs: <paths or IDs>
Design and input/output contract: <only what workers need>
Behavior oracle: <user-visible acceptance>
Global decisions: <only remaining decisions needed before work starts>

GATE
Decision: ACCEPT | REVISE | BLOCK
Reason code: <one code>
Required delta: <minimal change or none>
Next owner: <lane/worker>

FINAL
Verdict: ACCEPT | REVISE | BLOCK
Evidence: <checkpoint/diff/test refs>
Behavior validation: <contract verdict>
Blockers: <material only>
Residual risk: <material only>
```

Use Luna or the deterministic checkpoint helper to normalize mechanical result material before these envelopes. The primary coordinator normally starts from the compact packet and may inspect raw worker output whenever direct evidence would improve design, behavioral validation, or project review.

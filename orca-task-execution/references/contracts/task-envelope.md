# Common Task Envelope

Read once before creating delegated Tasks. Domain and role contracts add constraints; they never widen this envelope.

## Required header

Every Task begins exactly:

```text
[execution-owner: skill=orca-task-execution]
[task-domain: software|reverse]
[worker-role: terra|luna]
Task: <id>
```

`mixed` is forbidden as a worker domain. Model and effort are omitted because the dispatch script derives them from domain and role.

## Closed authority

Objective and acceptance describe the desired result; they do not grant authority beyond explicit target/lane, read/write or mutation scope, batch/evidence budget, expansion allowance, and decision role. Transitive discoveries remain outside scope. Reusing a warm terminal preserves context, not authority.

When completion requires broader authority, preserve in-scope work and return one request:

```text
NEED_SCOPE: exact additional targets/files/symbols/ranges and why
NEED_BULK_EVIDENCE: manifest/query/schema/coverage/raw-reference requirements
NEED_CONTRACT_DECISION: evidence and shared behavior/API/security/data decision
NEED_GLOBAL_DECISION: evidence and global algorithm/protection/policy decision
NEED_DOMAIN_SPLIT: exact evidence-to-implementation output boundary
```

Only the primary coordinator approves deltas or creates cross-domain Tasks.

## Compact Task

```text
Objective: <one independently verifiable outcome>
Context: <Run Context ref/version + minimum fallback facts>
Lane/target: <cohesive software lane or exact reverse target>
Contract: <inputs, outputs, invariants, behavior/evidence oracle>
Starts: <exact paths/symbols/artifacts/addresses/commands>
Batch/evidence slice: <bounded manifest or none>
Depends: <Task IDs or none>
Read: <bounded logical scopes>
Write: <bounded scopes; none for read-only>
Forbidden: <changes, decisions, targets, evidence, or behaviors>
Scope mode: closed
Expansion allowance: <none or exact named additions>
Decision authority: <cohesive lane semantics or frozen-contract processing>
Acceptance: <observable checks and evidence>
Escalate: <conditions invalidating domain, role, scope, or contract>
Return: <normalized report path, result, validation, context delta, risks, requests>
```

## Result

Non-trivial work produces a durable compact report containing Task/status, domain/role and derived profile, context/artifact revision, actual scopes inspected or changed, acceptance/evidence, decisions inside authority, deviations, risks, requests, next action, and a short summary. `worker_done` contains at most status, acceptance/blocker, and report path—never raw logs, dumps, transcripts, or copied source.

## TaskGraphLite

```json
{
  "execution_owner_skill": "orca-task-execution",
  "run_domain": "software",
  "tasks": [
    {
      "id": "T1",
      "domain": "software",
      "role": "terra",
      "depends_on": [],
      "read": ["src/auth/**"],
      "write": ["src/auth/service.ts"],
      "risk": "medium"
    }
  ]
}
```

Validate useful sidecars with `scripts/validate_task_graph.py`. The graph records orchestration facts, not coordinator reasoning.

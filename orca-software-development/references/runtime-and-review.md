# Orca Runtime and Review

Load only for delegated execution, lifecycle recovery, placement decisions, or review/escalation.

## 1. Live contract first

Before Orca operations, read the installed `orca-cli` and `orchestration` skills and follow their version-matched guide. This reference intentionally does not duplicate command syntax.

Orca owns live Run/Task/Dispatch/message state. Git commits and diffs are durable implementation evidence.

## 2. Worker profile persistence

Every worker Task starts with exactly one persisted profile:

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
```

For launch, retry, replacement, or resumed work:

1. re-read the Task profile;
2. launch with that exact profile as the live guide requires;
3. verify requested and effective profile in the launch receipt;
4. treat mismatch as launch failure, not permission to silently downgrade;
5. reuse an existing terminal only when Orca proves it has the same effective profile and reuse is valid.

After a long wait, context compaction, or coordinator restart, reconstruct state from live Orca Tasks/Dispatches plus Git, not coordinator memory.

## 3. Placement

- Single writable worker: current worktree is preferred when safe, especially when user-owned uncommitted state matters.
- Read-only workers: may share the same worktree when their tools do not mutate project state.
- Concurrent writable workers: keep them in the required current or exact existing worktree unless the user explicitly requests isolation or a concrete conflict involving checkout state, generated files, index/HEAD, build outputs, fixtures, or other mutable global state makes sharing unsafe or impossible. State that conflict before creating a worktree.

Do not create worktrees merely to appear more parallel.

## 4. Supervised loop

Create independent ready Tasks before waiting. Follow the live guide to start workers and retain Task/Dispatch provenance.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- For ordinary development work, use a window of at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit. Do not use short rolling windows merely to keep the coordinator active. Matching `worker_done`, `escalation`, or `question` messages wake the wait early, so a long timeout does not delay handling them.
- Keep exactly one Orca lifecycle wait in flight for the Run. If the host command runner returns a still-running process/session handle, continue that same process/session. Do not launch another Orca check alongside it.
- Treat transport `_keepalive` or `_heartbeat` frames as evidence that the same call is still active, not as lifecycle messages, completion, timeout, or a reason to inspect workers.
- Treat a no-message timeout as one liveness checkpoint, not worker failure. After it, use at most one cheap aggregate Run/task check before starting the next long wait. Inspect an individual terminal only when aggregate state shows a concrete anomaly that requires it.
- Use a shorter window only for an explicit user deadline or another concrete workflow deadline; never shorten it for routine progress visibility.

The primary coordinator agent must not poll a running worker between these checkpoints or spend primary-coordinator context on terminal output unless a concrete decision requires a coordinator reason code.

Keep a cohesive Task active across local clarification and ordinary repair. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

## 5. Result routing

Classify before choosing another model:

| Result | Route |
|---|---|
| Ordinary local defect within contract | Same worker, delta-only retry |
| Known mechanical correction | Luna Max |
| Unknown cause / expanded implementation | Terra XHigh |
| Shared contract or architecture invalid | Primary coordinator agent |
| Security/data/concurrency global decision | Primary coordinator agent |
| Cross-task conflict | Primary coordinator agent |

Changing agents unnecessarily repays repository and problem-understanding cost.

## 6. Review gates

### Local accept

Use for low-risk bounded work when:

- write scope matches contract;
- acceptance evidence is complete;
- targeted tests/checks pass;
- no shared interface changed unexpectedly;
- no material risk or unresolved question remains.

No individual high-tier coordinator review is required.

### Integration review

Use when multiple accepted changes interact. Terra or the coordinator checks aggregate diff, interfaces, repository invariants, and the broader test plan.

### Coordinator review

Use once when work is medium/high risk, cross-cutting, changes important contracts, or triggers another coordinator reason code. Send a compact review packet and diff references, not worker transcripts.

## 7. Checkpoint and resume

Before high-tier review or after a substantial wave, compact results into:

```text
Run/base/integration head
Tasks done/blocked/failed
Accepted commits and changed files
Acceptance/test evidence
Accepted decisions and new facts
Risks/questions
Next actions
```

Drop raw logs and conversations. If persistent recovery is needed, store only compact checkpoints/decision references in Git or Orca comments; do not turn Git into a message database.

## 8. Termination

Finish when required acceptance passes, required review gates accept, all Dispatches are accounted for, and material risks are resolved. Do not stop because an observational usage target was exceeded.

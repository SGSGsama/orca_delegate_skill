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

Treat the Terra terminal as the composer and context owner of its semantic lane, not as a disposable phase worker. Before release, check whether the accepted result has an immediate inspect/implement/compose/test/repair continuation in the same lane; if so, create the next Task from the lane delta and reuse that exact terminal. A lower nominal Luna price does not justify discarding warm Terra context.

## 3. Placement

- Single writable worker: current worktree is preferred when safe, especially when user-owned uncommitted state matters.
- Read-only workers: may share the same worktree when their tools do not mutate project state.
- Concurrent writable workers: keep them in the required current or exact existing worktree unless the user explicitly requests isolation or a concrete conflict involving checkout state, generated files, index/HEAD, build outputs, fixtures, or other mutable global state makes sharing unsafe or impossible. State that conflict before creating a worktree.

Do not create worktrees merely to appear more parallel.

## 4. Supervised loop

Create independent ready Tasks before waiting. Follow the live guide to start workers and retain Task/Dispatch provenance.

### Delivery gate

Pass this gate once for every new or reused worker Dispatch before entering the lifecycle wait:

1. Prefer the live guide's composed worker-start path. Use low-level terminal creation and delivery only when the composed path cannot express the required topology or launch profile.
2. For a low-level path, wait until the intended agent TUI is ready, then use the live guide's submission behavior. Text appearing in the input control is staged input, not accepted work; delivery includes the submit/Enter action.
3. Read the delivery receipt and perform one bounded post-delivery observation. Confirm the Task and Dispatch target the expected worker and that the worker has left the staged input state and begun processing. Only then start the Run-level wait.
4. If the complete Task text is still staged, submit the existing buffer exactly once using the live guide. Do not type the Task again, create a second Dispatch, or start another worker. If submission cannot be proven, report a delivery failure instead of waiting for a completion that cannot arrive.

This one-time delivery observation is not ongoing worker polling and must not be repeated after processing is established.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- For ordinary development work, use a window of at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit. Do not use short rolling windows merely to keep the coordinator active. Matching `worker_done`, `escalation`, or `question` messages wake the wait early, so a long timeout does not delay handling them.
- Keep exactly one Orca lifecycle wait in flight for the Run. If the host command runner returns a still-running process/session handle, continue that same process/session. Do not launch another Orca check alongside it.
- Treat transport `_keepalive` or `_heartbeat` frames as evidence that the same call is still active, not as lifecycle messages, completion, timeout, or a reason to inspect workers.
- Treat a no-message timeout as one liveness checkpoint, not worker failure. After it, use at most one cheap aggregate Run/task check before starting the next long wait. Inspect an individual terminal only when aggregate state shows a concrete anomaly that requires it.
- Use a shorter window only for an explicit user deadline or another concrete workflow deadline; never shorten it for routine progress visibility.

Avoid primary-coordinator polling or terminal inspection between these checkpoints. Inspect directly when aggregate state exposes an anomaly, the user asks, or a material decision genuinely needs the underlying output.

Keep a cohesive Task active across local clarification and ordinary repair. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

### Coordinator communication budget

- Create Tasks per independent acceptance unit. Put bounded repetitive items into one Luna batch instead of creating per-file, per-test, or per-item lifecycle traffic.
- Require a normalized report artifact for non-trivial results. Keep `worker_done` to at most three short sentences: status, acceptance/blocker, and report path. Never put raw logs or a full analysis in the Run inbox.
- Process low-risk successful Luna messages mechanically under local acceptance by default; add primary-coordinator review or user-facing detail when it materially helps acceptance or the user requests it.
- After a wave, run the deterministic compactor once. Use a Luna normalization Task only when reports need non-trivial classification that the script cannot perform. Produce one checkpoint for the wave before Terra composer integration or primary-coordinator review.
- Workers resolve local questions inside delegated authority. A Luna batch records item-level exceptions and continues safe independent items; send one grouped escalation only when a global contract or decision blocks the batch.
- Default primary-coordinator communication covers the initial shape/global decisions, reason-code-triggered gates, material blockers, and the final project verdict. Keep lifecycle receipts and ordinary progress in Orca state unless surfacing them would help the user or a decision.

## 5. Result routing

Classify before choosing another model:

| Result | Route |
|---|---|
| Ordinary local defect or follow-up within a warm lane | Same worker, delta-only retry |
| Known mechanical correction | Luna Max |
| Unknown cause / expanded implementation / leaf integration | Terra XHigh composer |
| Shared contract or architecture invalid | Primary coordinator agent |
| Security/data/concurrency global decision | Primary coordinator agent |
| Cross-task conflict | Primary coordinator agent |

Changing agents unnecessarily repays repository and problem-understanding cost.

Route a mechanical correction to Luna only when its compact input contract is sufficient to avoid broad rediscovery. Otherwise keep it with the warm Terra composer even if Luna compute is cheaper.

## 6. Review gates

### Local accept

Use for low-risk bounded work when:

- write scope matches contract;
- acceptance evidence is complete;
- targeted tests/checks pass;
- no shared interface changed unexpectedly;
- no material risk or unresolved question remains.

No individual high-tier coordinator review is required.

### Composer integration review

Use when multiple accepted changes interact. The primary coordinator attaches accepted Luna artifact references to a Terra composition Task; Terra does not create nested orchestration. Terra composes the lane result and checks the aggregate diff, interfaces, repository invariants, and broader test plan. Escalate to the primary coordinator when the integrated result changes the design/input-output contract or when final user-visible behavior must be accepted.

### Coordinator behavioral and project review

Use the primary coordinator to validate the integrated result against the accepted inputs, outputs, invariants, and user-visible behavior. Prefer one aggregated final project review when work is medium/high risk, cross-cutting, changes important contracts, or triggers another coordinator reason code; add intermediate coordinator review when it materially reduces risk. Start with a compact review packet and diff references, then inspect deeper evidence as needed. Keep the verdict focused on the contract/behavior decision, evidence references, material blockers, and residual risk.

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

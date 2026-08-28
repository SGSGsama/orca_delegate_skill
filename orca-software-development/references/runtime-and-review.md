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

Start every fresh worker through [the profiled dispatch script](../scripts/dispatch_profiled_worker.sh). Resolve its absolute path from the loaded `SKILL.md`; do not assume the target repository has a `scripts/` directory:

```bash
<skill-directory>/scripts/dispatch_profiled_worker.sh --task <task_id> --worktree current
```

The script reads the full Task spec from the bound Run and permits only `codex/gpt-5.6-terra/xhigh` or `codex/gpt-5.6-luna/max`. It rejects missing, malformed, downgraded, or caller-overridden profiles before launch, calls the composed `worker-start` path, and checks both `launch.requested` and `launch.effective`. Do not reconstruct a profile from coordinator memory or call fresh `worker-start` directly, including after compaction. A nonzero script result may still describe residual or live resources; follow its JSON receipt and do not retry automatically.

For launch, retry, replacement, or resumed work:

1. re-read the Task profile;
2. for a fresh terminal, launch through the profiled dispatch script with that exact profile;
3. verify requested and effective profile in the launch receipt;
4. treat mismatch as launch failure, not permission to silently downgrade;
5. reuse an existing terminal only when `worker-show` proves it has the same effective profile and reuse is valid; the script intentionally rejects `--terminal` because model/effort cannot be reapplied there.

After a long wait, context compaction, or coordinator restart, reconstruct durable facts from live Orca Tasks/Dispatches plus Git, not free-form coordinator memory. Maintain this minimal transient resume capsule in compact turn state:

```text
role=primary_coordinator
run_id=<id> context_version=<version-or-ref>
accepted_contracts=<refs> outstanding=<Task/Dispatch/profile/warm-terminal tuples>
profiled_dispatch=<absolute skill script path> fresh_launch=script_only
delivery_gate=<passed-or-not-applicable>
wait_epoch=<id> think_before_wait=<consumed-or-pending>
wait_state=<active|none> wait_handle=<exact live host handle>
event_filter=<full version-matched filter, including question when supported> timeout_ms=<selected interval>
wake_on=delivery|true_timeout|wait_failure|user
next_action=<resume_same_wait-or-explicit lifecycle action>
model_observation=silent_until_event
```

This is control state, not a progress narrative. Preserve exact identifiers, model/effort profiles, the absolute profiled-dispatch path and script-only fresh-launch policy, the full lifecycle filter, and consumed gates; a resume must not silently downgrade effort or drop a message type such as `question`. Do not recreate or reinterpret these fields after compaction. If `wait_state=active`, execute only `next_action=resume_same_wait` until a `wake_on` event occurs. The timeout is runtime control state, not a model countdown. If the saved host handle is explicitly invalid after restart, enter wait-failure recovery once rather than guessing or creating parallel waiters. Never persist transient process handles in Git.

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
2. For a low-level path, wait until the intended agent TUI is ready, then use the live guide's atomic send-and-submit behavior. Include submit/Enter in the same terminal-delivery action as the Task text. Never stage text now and plan to press Enter in a later coordinator turn. If the runtime exposes only separate input and submit actions, perform them as one uninterrupted delivery sequence before commentary, waiting, or any unrelated operation.
3. Read the delivery receipt and perform one bounded post-delivery observation. Confirm the Task and Dispatch target the expected worker and that the worker has left the staged input state and begun processing. Only then start the Run-level wait.
4. If the complete Task text is still staged, submit the existing buffer exactly once using the live guide. Do not type the Task again, create a second Dispatch, or start another worker. If submission cannot be proven, report a delivery failure instead of waiting for a completion that cannot arrive.

This one-time delivery observation is not ongoing worker polling and must not be repeated after processing is established.

### Think once before waiting

Before a new long wait after the initial Dispatch wave, a processed actionable Delivery, or a true timeout, pause once to reconsider the work. One lifecycle transition permits one pass; anything considered or selected by that pass does not recursively trigger another pass.

Use only accepted Run Context, current acceptance gaps, and already available durable evidence. The coordinator may think through next steps, solution or research approaches, design/behavior/acceptance and integration plans, what remains blocked, or whether another useful independent Task has emerged. This reflection need not create an artifact or change the plan. Do not read active worker terminals or partial output, reopen settled decisions, perform broad repository discovery, or create optional polish merely to keep the coordinator busy.

If the pass reveals one clearly useful bounded coordinator action, the coordinator may perform it at a natural checkpoint. If it reveals stable independent work that clearly advances the critical path or material risk reduction, does not depend on unaccepted worker output, does not duplicate/conflict with active scope, and repays context and integration cost, create the minimum cohesive additional Dispatch wave. Otherwise start the long wait immediately.

Thinking does not imply dispatch. Do not manufacture work, force a plan change, or perform repeated passes to maximize utilization.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- **Choose the interval once.** When the first Dispatch becomes active, choose and record one global liveness interval based on expected task duration, user deadlines, and runtime reliability. It must normally be at least 15 minutes (`900000 ms`); 30-60 minutes is appropriate for longer work. If Orca itself imposes a lower maximum, use that maximum. A host command-runner yield limit is not an Orca timeout limit. Do not shorten the interval for visibility or to keep the coordinator active.
- **Start one wait.** Use the selected interval as `check --wait`'s timeout. Matching lifecycle messages wake it early, so a long timeout does not delay handling. This interval is the coordinator's liveness-check cadence, not the transport or worker heartbeat cadence.
- **Live wait state.** If the host returns a still-running process/session handle, resume that exact handle using the longest host blocking interval available. `_keepalive`, `_heartbeat`, partial command output, and command-runner yield mean the same wait is alive. Transport keepalive cadence is runtime-owned and may be fixed; do not try to change it through the selected liveness interval. When the version-matched guide exposes a supported keepalive filter, use it when useful without hiding the final Delivery or real command errors. A no-event resume requires no coordinator interpretation: do not derive elapsed or remaining time, window fraction, deadline proximity, connection health, or worker/process health; do not launch another Orca command, inspect Run/task/terminal state, or emit wait-progress commentary. Tool-generated background-terminal records are acceptable and do not change this rule.
- **Delivery state.** Process every message in the bounded Delivery. Reply to questions and account for each completed worker by reuse, retention, or release before acknowledgement. If none remain, acknowledge without starting another wait. If Dispatches remain, think once before waiting. When no execution or dispatch follows, use the live guide's combined acknowledgement-and-wait path with the selected interval after recording any useful plan delta. When a bounded action was selected, acknowledge without waiting, complete it, then start exactly one wait without thinking again.
- **True-timeout state.** Only a completed result that reports an actual no-message timeout or `{count:0}` ends the wait without a Delivery. It is a liveness checkpoint, not worker failure. Perform at most one cheap aggregate Run/task query when useful, think once before waiting, then start exactly one new wait with the selected interval if Dispatches remain outstanding. Complete any selected bounded action first, without another reflection pass afterward.
- **Wait-failure state.** A cancellation, connection loss, or explicit command failure ends the host wait but does not prove worker failure. Follow the exact runtime recovery guidance and re-establish at most one Run-level waiter; do not substitute worker-terminal polling.
- **Exceptional inspection.** Inspect an individual terminal only when aggregate state identifies a concrete anomaly requiring terminal evidence, the user explicitly requests it, or a material global decision genuinely depends on partial output.

This state machine intentionally narrows the live guide's generic suggestion to inspect state after an empty wait window: only completion of the coordinator's selected long interval qualifies here. The live guide remains authoritative for Delivery ordering, acknowledgement, questions, and worker reuse/release.

Keep a cohesive Task active across local clarification and ordinary repair. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

### Coordinator communication budget

- Filter transport keepalive at the command/tool boundary when convenient, but do not spend coordinator reasoning or narration on transport records that remain visible. Do not request routine worker heartbeat/status messages. When the live preamble or a concrete reliability risk requires heartbeats, choose one long Run-level cadence no shorter than the selected liveness interval and send only meaningful phase changes.
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
- actual files and evidence inspected remain inside the coordinator-approved envelope;
- acceptance evidence is complete;
- targeted tests/checks pass;
- no shared interface changed unexpectedly;
- no material risk or unresolved question remains.

No individual high-tier coordinator review is required.

An undeclared read/write/evidence expansion or a worker-made shared-contract decision is `REVISE` even when targeted tests pass.

### Composer integration review

Use when multiple accepted changes interact. The primary coordinator attaches accepted Luna artifact references to a Terra composition Task; Terra does not create nested orchestration. Terra composes the lane result and checks the aggregate diff, interfaces, repository invariants, and broader test plan. Escalate to the primary coordinator when the integrated result changes the design/input-output contract or when final user-visible behavior must be accepted.

### Coordinator behavioral and project review

Use the primary coordinator to validate the integrated result against the accepted inputs, outputs, invariants, and user-visible behavior. Prefer one aggregated final project review when work is medium/high risk, cross-cutting, changes important contracts, or triggers another coordinator reason code; add intermediate coordinator review when it materially reduces risk. Start with a compact review packet and diff references, then inspect deeper evidence as needed. Keep the verdict focused on the contract/behavior decision, evidence references, material blockers, and residual risk.

## 7. Checkpoint and resume

Before high-tier review or after a substantial wave, compact results into:

```text
Run/base/integration head
Selected liveness interval and last true timeout/checkpoint
Outstanding Task/Dispatch IDs and persisted worker profiles
Tasks done/blocked/failed
Accepted commits and changed files
Acceptance/test evidence
Accepted decisions and new facts
Risks/questions
Next actions
```

Refresh the durable checkpoint and transient resume capsule only after a real lifecycle transition, Dispatch/accounting change, accepted decision, or user instruction—not after keepalive, host yield, or compaction itself. Drop raw logs and conversations. If persistent recovery is needed, store only compact checkpoints/decision references in Git or Orca comments; do not turn Git into a message database.

## 8. Termination

Finish when required acceptance passes, required review gates accept, all Dispatches are accounted for, and material risks are resolved. Do not stop because an observational usage target was exceeded.

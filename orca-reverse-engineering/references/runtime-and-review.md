# Orca Runtime and Reverse-Engineering Synthesis

Load only for delegated execution, lifecycle recovery, artifact placement, mutation decisions, or acceptance/synthesis.

## 1. Live contract first

Before Orca operations, read the installed `orca-cli` and `orchestration` skills and follow their version-matched guide. This reference intentionally does not duplicate command syntax.

Orca owns live Run/Task/Dispatch/message state. Artifact digests, database revisions, exports, reports, and Git commits/diffs are durable evidence.

## 2. Worker profile persistence

Every worker Task starts with exactly one persisted profile:

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
```

For launch, retry, replacement, or resumed work:

1. re-read the Task profile;
2. launch with that exact profile as the live guide requires;
3. verify requested and effective profile in the launch receipt;
4. treat mismatch as launch failure, not permission to silently downgrade;
5. reuse an existing terminal only when Orca proves it has the same effective profile and reuse is valid.

After a long wait, context compaction, or coordinator restart, reconstruct durable facts from live Orca Tasks/Dispatches plus durable artifact evidence, not free-form coordinator memory. Maintain this minimal transient resume capsule in compact turn state:

```text
role=primary_coordinator
run_id=<id> context_version=<version-or-ref>
accepted_global_model=<refs> outstanding=<Task/Dispatch/profile/warm-terminal tuples>
delivery_gate=<passed-or-not-applicable>
wait_epoch=<id> think_before_wait=<consumed-or-pending>
wait_state=<active|none> wait_handle=<exact live host handle>
event_filter=<full version-matched filter, including question when supported> timeout_ms=<selected interval>
wake_on=delivery|true_timeout|wait_failure|user
next_action=<resume_same_wait-or-explicit lifecycle action>
model_observation=silent_until_event
```

This is control state, not a progress narrative. Preserve exact identifiers, artifact/database revisions, model/effort profiles, the full lifecycle filter, accepted hypotheses, and consumed gates; a resume must not silently downgrade effort or drop a message type such as `question`. Do not recreate or reinterpret these fields after compaction. If `wait_state=active`, execute only `next_action=resume_same_wait` until a `wake_on` event occurs. The timeout is runtime control state, not a model countdown. If the saved host handle is explicitly invalid after restart, enter wait-failure recovery once rather than guessing or creating parallel waiters. Never persist transient process handles in Git or analysis artifacts.

Treat a Terra terminal as the context owner of its bounded local target, not as a disposable phase worker. Before release, check whether an adjacent function, local hypothesis, or evidence gap uses substantially the same target context; if so, create the next Task from the local delta and reuse that exact terminal. Do not make a replacement analyst reload the same functions, IL, tool state, and evidence slices.

## 3. Artifact placement and mutation

- One mutation worker: use the required current or exact existing worktree and analysis context when safe, especially when user-owned uncommitted artifacts matter.
- Read-only workers: may share the same worktree, binaries, exports, and databases only when the tools and database access modes are non-mutating.
- Concurrent mutation against one analysis database, GUI session, trace store, or output file: serialize by default. Separate Git worktrees do not isolate external application state.
- Isolated copies: use only when the user requests them or a concrete checkout/filesystem conflict requires them, and only with an explicit identity, revision, and merge/acceptance strategy.

Do not create worktrees merely to appear more parallel.

## 4. Supervised loop

Create independent ready Tasks before waiting. Follow the live guide to start workers and retain Task/Dispatch provenance.

### Delivery gate

Pass this gate once for every new or reused worker Dispatch before entering the lifecycle wait:

1. Prefer the live guide's composed worker-start path. Use low-level terminal creation and delivery only when the composed path cannot express the required topology or launch profile.
2. For a low-level path, wait until the intended agent TUI is ready, then use the live guide's atomic send-and-submit behavior. Include submit/Enter in the same terminal-delivery action as the investigation text. Never stage text now and plan to press Enter in a later coordinator turn. If the runtime exposes only separate input and submit actions, perform them as one uninterrupted delivery sequence before commentary, waiting, or any unrelated operation.
3. Read the delivery receipt and perform one bounded post-delivery observation. Confirm the Task and Dispatch target the expected worker and that the worker has left the staged input state and begun processing. Only then start the Run-level wait.
4. If the complete investigation text is still staged, submit the existing buffer exactly once using the live guide. Do not type the investigation again, create a second Dispatch, or start another worker. If submission cannot be proven, report a delivery failure instead of waiting for a completion that cannot arrive.

This one-time delivery observation is not ongoing worker polling and must not be repeated after processing is established.

### Think once before waiting

Before a new long wait after the initial Dispatch wave, a processed actionable Delivery, or a true timeout, pause once to reconsider the investigation. One lifecycle transition permits one pass; anything considered or selected by that pass does not recursively trigger another pass.

Use only accepted global context, current evidence/acceptance gaps, and already available durable evidence. The coordinator may think through next investigations, research or recovery approaches, global hypotheses, algorithm/protection models, falsification or synthesis plans, what remains blocked, or whether another useful independent Luna/Terra Task has emerged. This reflection need not create an artifact or change the plan. Do not read active worker terminals or partial output, reopen settled hypotheses without new evidence, perform broad raw-input exploration, or create optional naming/comment work merely to keep the coordinator busy.

If the pass reveals one clearly useful bounded coordinator analysis, the coordinator may perform it at a natural checkpoint. If it reveals stable independent work that clearly advances the critical path or material uncertainty reduction, does not depend on unaccepted worker output, does not duplicate/conflict with active investigation or mutable analysis state, and repays context and synthesis cost, create the minimum cohesive additional Luna/Terra Dispatch wave. Otherwise start the long wait immediately.

Thinking does not imply dispatch. Do not manufacture investigations, force a hypothesis/plan change, or perform repeated passes to maximize utilization.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- **Choose the interval once.** When the first Dispatch becomes active, choose and record one global liveness interval based on expected investigation duration, user deadlines, and runtime reliability. It must normally be at least 15 minutes (`900000 ms`); 30-60 minutes is appropriate for long analysis. If Orca itself imposes a lower maximum, use that maximum. A host command-runner yield limit is not an Orca timeout limit. Do not shorten the interval for visibility or to keep the coordinator active.
- **Start one wait.** Use the selected interval as `check --wait`'s timeout. Matching lifecycle messages wake it early, so a long timeout does not delay handling. This interval is the coordinator's liveness-check cadence, not the transport or worker heartbeat cadence.
- **Live wait state.** If the host returns a still-running process/session handle, resume that exact handle using the longest host blocking interval available. `_keepalive`, `_heartbeat`, partial command output, and command-runner yield mean the same wait is alive. Transport keepalive cadence is runtime-owned and may be fixed; do not try to change it through the selected liveness interval. When the version-matched guide exposes a supported keepalive filter, use it when useful without hiding the final Delivery or real command errors. A no-event resume requires no coordinator interpretation: do not derive elapsed or remaining time, window fraction, deadline proximity, connection health, or worker/process health; do not launch another Orca command, inspect Run/task/terminal/raw-evidence state, or emit wait-progress commentary. Tool-generated background-terminal records are acceptable and do not change this rule.
- **Delivery state.** Process every message in the bounded Delivery. Reply to questions and account for each completed worker by reuse, retention, or release before acknowledgement. If none remain, acknowledge without starting another wait. If Dispatches remain, think once before waiting. When no execution or dispatch follows, use the live guide's combined acknowledgement-and-wait path with the selected interval after recording any useful plan delta. When a bounded action was selected, acknowledge without waiting, complete it, then start exactly one wait without thinking again.
- **True-timeout state.** Only a completed result that reports an actual no-message timeout or `{count:0}` ends the wait without a Delivery. It is a liveness checkpoint, not worker failure. Perform at most one cheap aggregate Run/task query when useful, think once before waiting, then start exactly one new wait with the selected interval if Dispatches remain outstanding. Complete any selected bounded action first, without another reflection pass afterward.
- **Wait-failure state.** A cancellation, connection loss, or explicit command failure ends the host wait but does not prove worker failure. Follow the exact runtime recovery guidance and re-establish at most one Run-level waiter; do not substitute worker-terminal or raw-evidence polling.
- **Exceptional inspection.** Inspect an individual terminal or raw evidence only when aggregate state identifies a concrete anomaly requiring that evidence, the user explicitly requests it, or a material global interpretation genuinely depends on partial output.

This state machine intentionally narrows the live guide's generic suggestion to inspect state after an empty wait window: only completion of the coordinator's selected long interval qualifies here. The live guide remains authoritative for Delivery ordering, acknowledgement, questions, and worker reuse/release.

Keep a cohesive investigation active across local clarification and ordinary evidence gaps. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

### Coordinator communication budget

- Filter transport keepalive at the command/tool boundary when convenient, but do not spend coordinator reasoning or narration on transport records that remain visible. Do not request routine worker heartbeat/status messages. When the live preamble or a concrete reliability risk requires heartbeats, choose one long Run-level cadence no shorter than the selected liveness interval and send only meaningful phase changes.
- Create Tasks per independently checkable evidence product or local semantic question. Put large logs, traces, dumps, candidate sets, and repetitive targets into Luna manifests/batches instead of creating per-event or per-address lifecycle traffic.
- Require durable result artifacts. A Luna report carries input coverage, evidence-index references, clusters, and exceptions; a Terra report carries one bounded semantic conclusion with cited evidence and residual ambiguity.
- Keep `worker_done` to at most three short sentences: status, evidence/blocker, and report path. Never place raw bulk inputs, full dumps, or copied decompilation in the Run inbox.
- Accept coverage-complete low-risk Luna extraction and well-evidenced bounded Terra conclusions without narrating each result. Compact the wave before global synthesis; the primary coordinator can drill into any raw source reference when needed.
- A Luna batch continues safe independent items and groups anomalies. A Terra analyst resolves questions within its local target. Escalate when interpretation becomes global, protection assumptions change, or evidence/mutation policy must change.
- Default primary-coordinator communication covers global hypotheses/decisions, material contradictions or blockers, and the final algorithm/behavior/protection synthesis. Keep ordinary lifecycle progress in Orca state unless it helps the user or a decision.

## 5. Result routing

Classify before choosing another model:

| Result | Route |
|---|---|
| Ordinary evidence gap or adjacent question inside one bounded target | Same Terra, delta-only follow-up |
| Precise function/cluster meaning or local data/control flow | Terra Max local analyst |
| More logs/traces/dumps/candidates or repetitive extraction needed | Luna Max evidence processor |
| Bulk evidence exposes a precise local anomaly | Terra Max with the referenced evidence slice |
| Approved broad name/type/comment propagation | Luna Max batch |
| Algorithm flow, system behavior, complex protection, or global model changes | Primary coordinator agent |
| Cross-target contradiction or evidence/mutation policy decision | Primary coordinator agent |

Changing agents unnecessarily repays artifact loading, tool orientation, decompilation, and target-understanding cost. Give Luna explicit input manifests and schemas; give Terra exact local targets and evidence slices.

## 6. Acceptance and synthesis gates

### Bulk evidence accept

Use for Luna evidence processing when:

- the input manifest and schema match the Task;
- processed/skipped coverage is explicit;
- output identifiers link back to raw sources;
- anomalies and malformed inputs are preserved;
- no new semantic interpretation is silently asserted.

No individual high-tier coordinator review is required.

### Local semantic accept

Use for Terra findings when the target remains bounded, cited evidence supports the conclusion, alternatives and confidence are recorded, and the finding does not silently change the global algorithm or protection model. The coordinator may accept it locally or use it as an input to global synthesis.

### Coordinator global and adversarial synthesis

Use the primary coordinator to reconstruct and validate algorithms, cross-function/cross-artifact behavior, global state/protocol meaning, and complex protection or anti-analysis interactions. Start with indexed Luna evidence and cited Terra conclusions, then inspect underlying code or raw evidence directly as needed. Keep final synthesis focused on the global model, causal flow, behavior validation, decisive evidence, contradictions, and residual uncertainty.

## 7. Checkpoint and resume

Before high-tier synthesis or after a substantial wave, compact results into:

```text
Run/context version and artifact identities
Analysis/database revision
Selected liveness interval and last true timeout/checkpoint
Outstanding Task/Dispatch IDs and persisted worker profiles
Tasks done/blocked/failed
Bulk input coverage and evidence-index references
Accepted local function/cluster conclusions
Global algorithm/behavior/protection conclusions
Accepted names/types/offsets/states/schemas
Verified mutations
Rejected hypotheses and contradictions
Risks/questions
Next investigations
```

Refresh the durable checkpoint and transient resume capsule only after a real lifecycle transition, Dispatch/accounting change, accepted decision or hypothesis, or user instruction—not after keepalive, host yield, or compaction itself. Drop raw logs, disassembly, pseudocode, full traces, and conversations. If persistent recovery is needed, store only compact checkpoints and decision/evidence references in Git or Orca comments; do not turn Git into a message database or copy binaries unnecessarily.

## 8. Termination

Finish when the requested reconstruction is evidence-backed, required synthesis gates accept, all Dispatches are accounted for, persistent mutations are verified, and material uncertainty is explicit. Do not stop because an observational usage target was exceeded.

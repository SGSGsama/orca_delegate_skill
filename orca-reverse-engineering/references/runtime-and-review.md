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

After a long wait, context compaction, or coordinator restart, reconstruct state from live Orca Tasks/Dispatches plus durable artifact evidence, not coordinator memory.

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
2. For a low-level path, wait until the intended agent TUI is ready, then use the live guide's submission behavior. Text appearing in the input control is staged input, not accepted work; delivery includes the submit/Enter action.
3. Read the delivery receipt and perform one bounded post-delivery observation. Confirm the Task and Dispatch target the expected worker and that the worker has left the staged input state and begun processing. Only then start the Run-level wait.
4. If the complete investigation text is still staged, submit the existing buffer exactly once using the live guide. Do not type the investigation again, create a second Dispatch, or start another worker. If submission cannot be proven, report a delivery failure instead of waiting for a completion that cannot arrive.

This one-time delivery observation is not ongoing worker polling and must not be repeated after processing is established.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- For ordinary reverse-engineering work, use a window of at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit. Do not use short rolling windows merely to keep the coordinator active. Matching `worker_done`, `escalation`, or `question` messages wake the wait early, so a long timeout does not delay handling them.
- Keep exactly one Orca lifecycle wait in flight for the Run. If the host command runner returns a still-running process/session handle, continue that same process/session. Do not launch another Orca check alongside it.
- Treat transport `_keepalive` or `_heartbeat` frames as evidence that the same call is still active, not as lifecycle messages, completion, timeout, or a reason to inspect workers.
- Treat a no-message timeout as one liveness checkpoint, not worker failure. After it, use at most one cheap aggregate Run/task check before starting the next long wait. Inspect an individual terminal or raw dump only when aggregate state shows a concrete anomaly that requires it.
- Use a shorter window only for an explicit user deadline or another concrete workflow deadline; never shorten it for routine progress visibility.

Avoid primary-coordinator polling, terminal inspection, or raw-dump review between these checkpoints. Inspect directly when aggregate state exposes an anomaly, the user asks, or a material interpretation genuinely needs the underlying evidence.

Keep a cohesive investigation active across local clarification and ordinary evidence gaps. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

### Coordinator communication budget

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

Drop raw logs, disassembly, pseudocode, full traces, and conversations. If persistent recovery is needed, store only compact checkpoints and decision/evidence references in Git or Orca comments; do not turn Git into a message database or copy binaries unnecessarily.

## 8. Termination

Finish when the requested reconstruction is evidence-backed, required synthesis gates accept, all Dispatches are accounted for, persistent mutations are verified, and material uncertainty is explicit. Do not stop because an observational usage target was exceeded.

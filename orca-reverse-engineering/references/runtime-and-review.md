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

## 3. Artifact placement and mutation

- One mutation worker: use the required current or exact existing worktree and analysis context when safe, especially when user-owned uncommitted artifacts matter.
- Read-only workers: may share the same worktree, binaries, exports, and databases only when the tools and database access modes are non-mutating.
- Concurrent mutation against one analysis database, GUI session, trace store, or output file: serialize by default. Separate Git worktrees do not isolate external application state.
- Isolated copies: use only when the user requests them or a concrete checkout/filesystem conflict requires them, and only with an explicit identity, revision, and merge/acceptance strategy.

Do not create worktrees merely to appear more parallel.

## 4. Supervised loop

Create independent ready Tasks before waiting. Follow the live guide to start workers and retain Task/Dispatch provenance.

Use one blocking Run-level lifecycle wait for all active workers rather than polling terminals or opening one waiter per worker.

- For ordinary reverse-engineering work, use a window of at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit. Do not use short rolling windows merely to keep the coordinator active. Matching `worker_done`, `escalation`, or `question` messages wake the wait early, so a long timeout does not delay handling them.
- Keep exactly one Orca lifecycle wait in flight for the Run. If the host command runner returns a still-running process/session handle, continue that same process/session. Do not launch another Orca check alongside it.
- Treat transport `_keepalive` or `_heartbeat` frames as evidence that the same call is still active, not as lifecycle messages, completion, timeout, or a reason to inspect workers.
- Treat a no-message timeout as one liveness checkpoint, not worker failure. After it, use at most one cheap aggregate Run/task check before starting the next long wait. Inspect an individual terminal or raw dump only when aggregate state shows a concrete anomaly that requires it.
- Use a shorter window only for an explicit user deadline or another concrete workflow deadline; never shorten it for routine progress visibility.

The primary coordinator agent must not poll a running worker between these checkpoints or spend primary-coordinator context on terminal output or raw dumps unless a concrete decision requires a coordinator reason code.

Keep a cohesive investigation active across local clarification and ordinary evidence gaps. Do not create another Task merely for the next conversational turn.

On valid completion, account for the worker according to Orca's lifecycle rules: reuse when an immediate same-profile context unit justifies it, otherwise release it. Do not manually infer or duplicate settled state.

## 5. Result routing

Classify before choosing another model:

| Result | Route |
|---|---|
| Ordinary local evidence gap within contract | Same worker, delta-only follow-up |
| Approved mechanical extraction/propagation | Luna Max |
| Unknown meaning / expanded local ambiguity | Terra Max |
| Shared structure, protocol, or global model invalid | Primary coordinator agent |
| Evidence or mutation policy decision | Primary coordinator agent |
| Cross-task contradiction | Primary coordinator agent |

Changing agents unnecessarily repays artifact loading, tool orientation, decompilation, and local problem-understanding cost.

## 6. Acceptance and synthesis gates

### Local evidence accept

Use for low-risk bounded findings when:

- target and access/mutation scope match the contract;
- cited evidence is sufficient to distinguish the stated hypotheses;
- confidence is calibrated and alternatives are recorded;
- no accepted shared interpretation changed unexpectedly;
- no material contradiction or unresolved risk remains.

No individual high-tier coordinator review is required.

### Synthesis review

Use when multiple accepted findings interact. Terra or the coordinator checks shared names/types/offsets, call and data flow, state/protocol consistency, artifact identities, mutation results, and aggregate evidence.

### Coordinator synthesis

Use once when work is medium/high risk, cross-cutting, protocol-wide, changes important interpretations or mutation policy, or triggers another coordinator reason code. Send a compact synthesis packet and evidence references, not worker transcripts or raw dumps.

## 7. Checkpoint and resume

Before high-tier synthesis or after a substantial wave, compact results into:

```text
Run/context version and artifact identities
Analysis/database revision
Tasks done/blocked/failed
Accepted conclusions and evidence references
Accepted names/types/offsets/states/schemas
Verified mutations
Rejected hypotheses and contradictions
Risks/questions
Next investigations
```

Drop raw logs, disassembly, pseudocode, full traces, and conversations. If persistent recovery is needed, store only compact checkpoints and decision/evidence references in Git or Orca comments; do not turn Git into a message database or copy binaries unnecessarily.

## 8. Termination

Finish when the requested reconstruction is evidence-backed, required synthesis gates accept, all Dispatches are accounted for, persistent mutations are verified, and material uncertainty is explicit. Do not stop because an observational usage target was exceeded.

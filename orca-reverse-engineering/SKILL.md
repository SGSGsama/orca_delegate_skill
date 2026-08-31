---
name: orca-reverse-engineering
description: >-
  Use Orca for reverse-engineering work whose uncertainty, scope, artifact
  count, hypothesis count, or parallelism justifies delegation: unknown
  function clusters, protocol or state-machine recovery, object layouts,
  crypto or serialization, cross-binary correlation, competing hypotheses,
  comprehensive reviews, and explicit requests for Orca, Terra/Luna,
  parallel, or multi-agent analysis. Also activate when a bounded lookup grows
  into multiple targets, artifacts, hypotheses, bulk evidence, or mutations,
  including after context compaction. This skill exclusively owns reverse-
  engineering Task execution shape and primary/Terra/Luna assignment; tool and
  method skills constrain how the assigned owner works but cannot assign
  ownership. Let the primary coordinator agent answer a bounded read-only lookup
  directly only while the exact target, single question, and evidence path
  remain clear. When delegating, send cohesive investigations with shared
  binary and project context so workers do not repeat global discovery.
metadata:
  version: "0.5.0"
---

# Orca Reverse Engineering

Complete reverse-engineering work with a user-facing global semantic coordinator, Terra local analysts, and Luna high-volume evidence processors. Evidence quality and required validation take precedence over usage.

## Establish the role

- With a live Orca Dispatch preamble and Task block, act only as that worker, follow the injected lifecycle, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as the primary coordinator. Own user interaction, the global target model, algorithm and behavior reconstruction, input/output and evidence contracts, investigation boundaries, complex protection/anti-analysis reasoning, interpretation and mutation policy, and final synthesis.
- Direct user instructions override inherited worker history. Never reuse settled lifecycle IDs.

A delegated Task is a closed authority envelope. Its objective and acceptance criteria do not authorize a worker to expand the stated target, read/mutation scope, evidence slice, or decision authority. Scope is defined by the artifacts, ranges, manifests, and semantic question explicitly supplied by the coordinator, not by everything transitively discovered while solving it. Stop the affected branch and return the applicable scope, bulk-evidence, or global-decision request instead of widening the investigation independently.

### Execution ownership authority — exclusive

For every reverse-engineering Task in scope, `$orca-reverse-engineering` is the sole authority for the execution shape, primary-coordinator/Terra/Luna ownership, worker profile, target, evidence budget, and ownership changes. Other active skills—including analysis tools such as `bn`, decompilers, debuggers, and research methods—are subordinate capability or procedure constraints. They may determine how the Orca-assigned owner acquires or interprets evidence, but they must not select, change, preserve, or justify Task ownership or the direct/delegated shape.

Record `execution_owner_skill: orca-reverse-engineering` in global Run Context and TaskGraphLite. Every delegated Task must carry `[execution-owner: skill=orca-reverse-engineering]` immediately after its worker-profile line. Do not cite another skill as Task execution owner. When an investigation produces source, test, build, packaging, or implementation work, route that separately bounded Task to `$orca-software-development`; reverse-engineering evidence and reconstruction remain owned here.

## Route by semantic scope and input shape

- **Primary coordinator agent** — directly own globally coupled or adversarial reasoning: algorithm/control-flow reconstruction, system-wide behavior, complex obfuscation or hardening countermeasures, cross-function/cross-artifact interpretation, competing global hypotheses, and final validation. Avoid routine extraction and lifecycle narration, but do not delegate away the hardest semantic core merely to create Tasks.
- **Terra local analyst** — own bounded semantic targets such as one function or a tightly coupled function cluster, local data/control flow, calling conventions, localized object fields or state transitions, and evidence-backed naming/typing. Reuse the same valid terminal for coordinator-issued adjacent questions that share the same local target context.
- **Luna evidence processor** — own high-volume or low-semantic-density inputs such as logs, traces, dumps, string/xref/constant sets, large candidate lists, corpus comparisons, repetitive classifications, coverage accounting, and result normalization. Return indexed evidence and exceptions, not raw input copied into coordinator messages.

These are routing dimensions, not exhaustive task lists. Prefer coordinator-led global synthesis, a bounded Terra analysis, a batched Luna evidence pass, or a mixed Run according to semantic coupling, target locality, and input volume. Cheap Luna capacity does not justify per-line, per-address, or per-event Tasks.

Direct lookup ownership is not sticky. Before continuing, revoke and re-route it when the work ceases to be read-only, the exact target/question/evidence path expands, a second independent target or hypothesis appears, bulk evidence or repeated cases are needed, or source implementation begins. Coordinator-initiated scope expansion is a new routing event. Globally coupled semantic synthesis may remain with the primary coordinator only as an explicit `$orca-reverse-engineering` ownership decision; route bounded local semantics to Terra and high-volume evidence to Luna. After context compaction, perform this ownership check before further inspection or mutation; if the recorded direct basis cannot still be proved, revoke direct lookup ownership and establish the appropriate Run shape.

Read [references/decomposition.md](references/decomposition.md) whenever routing, lane boundaries, batching, or parallel safety is not obvious.

## Build context once

Pay global target discovery once per Run. The primary coordinator keeps the execution ownership skill, current execution shape, direct basis and revocation state when applicable, global model, and hypothesis ledger. Luna receives bulk-input manifests plus an extraction/coverage schema; Terra receives exact functions, addresses, local questions, and relevant evidence slices. Pass references and deltas, not coordinator transcripts, raw dumps, or repeated global discovery.

Use the evidence pipeline when useful: Luna indexes large inputs, Terra resolves bounded local semantics, and the primary coordinator integrates those results into algorithms, behaviors, and protection-countermeasure conclusions. Skip stages that add no evidence. Keep each Terra target cohesive and each Luna batch broad enough to amortize lifecycle and input-loading cost.

Before creating any delegated Task, read [references/task-contracts.md](references/task-contracts.md) and persist its exact Luna or Terra model/effort profile in the Task.

## Run Orca safely

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Complete the delivery gate once: prove the intended Dispatch exists and the worker has begun processing; staged text without submission is not delivery. On a low-level terminal path, input and submit/Enter are one atomic delivery action—never yield the coordinator turn with the investigation still in the worker's input box.

For every fresh supervised worker launch, use [scripts/dispatch_profiled_worker.sh](scripts/dispatch_profiled_worker.sh) instead of calling `orca orchestration worker-start` directly. The script reloads the Task's first-line profile and second-line execution owner from Orca state, rejects ownership by any skill except `orca-reverse-engineering`, rejects any tuple outside this skill's fixed Terra/Luna allowlist before launch, supplies its agent/model/effort, and fails closed unless the launch receipt proves identical requested and effective profiles. This remains required after context compaction. Terminal reuse is the only exception because Orca cannot change model/effort on `--terminal`; reuse only after the next Task declares this same execution owner and `worker-show` proves that the retained terminal's effective profile exactly matches the Task and one of the same allowed tuples.

### Event-driven worker waiting — required

Before starting a new long Run-level wait—after the initial Dispatch wave, an actionable Delivery, or a true timeout—pause once for a bounded think-before-wait pass from accepted Run Context. Reconsider next investigations, research or recovery approach, global hypotheses, falsification/evidence gaps, and useful coordinator-owned algorithm or adversarial reasoning. The pass may simply improve the investigation plan, perform one bounded analysis, identify a stable independent Luna/Terra Task worth dispatching, or conclude that waiting is correct; it need not produce new work. Do not repeat it for keepalive, command-runner yield, live-session resume, coordinator idleness, or ordinary completion of work selected by the same pass.

When the first Dispatch becomes active, choose one long Run-level liveness interval appropriate to the expected investigation duration and record it in the compact Run Context. It must normally be at least 15 minutes (`900000 ms`); longer intervals are encouraged for long analyses. Use that interval as the Orca lifecycle-wait timeout for all active workers.

Keep exactly one Run-level blocking wait in flight. A command-runner yield, keepalive, heartbeat, or coordinator idleness does not end it: resume the exact live process/session with the longest supported host wait, suppress transport-only frames with the live guide's supported filter when useful, and remain silent when it contains no lifecycle event. While that wait is alive, do not calculate, compare, or narrate elapsed time, remaining time, window fractions, deadline proximity, connection health, or worker/process health from transport or wait metadata. Tool-generated background-terminal records may remain visible; they are not coordinator work or a reason to comment. Do not issue another Orca command or status query while that wait is alive.

Carry the runtime reference's compact resume capsule across long waits and context compaction. Treat it as control state: compaction alone must not change the primary-coordinator role, accepted global model, worker profiles, profiled-dispatch script path/policy, event filter, outstanding Dispatch accounting, delivery-gate status, consumed think-before-wait pass, or next legal action. In particular, it must not cause a new waiter, re-dispatch, another reflection pass, local evidence inspection, or status query.

Only an actionable Delivery, a true completed wait timeout, or an explicit wait failure/cancellation changes coordinator state. Process and acknowledge a Delivery under the live Orca contract. After a true timeout, perform at most one aggregate Run/task liveness check and start one new wait only if Dispatches remain outstanding. Follow exact runtime recovery for a failed wait without inferring worker failure. Do not poll individual workers or raw dumps unless aggregate state exposes a concrete anomaly, the user asks, or a material interpretation needs their evidence. This stricter policy narrows generic per-window liveness suggestions in the live guide; its Delivery, acknowledgement, and worker-accounting rules still apply.

Minimize primary-coordinator input at the source. Admit actionable lifecycle messages, compact decision evidence, and allowed aggregate checkpoints; filter transport frames, repeated receipts, routine status, and raw worker output before they enter coordinator context. Do not request routine worker heartbeats. When a live preamble or concrete reliability risk requires them, choose a long Run-level cadence and report phase changes rather than unchanged aliveness.

Reuse a warm Terra analyst for the same local target. Batch Luna work by input source and evidence question, locally accept coverage-complete low-risk extraction, and compact each wave before global synthesis. The coordinator may inspect any underlying evidence when useful, while default user-facing output stays decision-focused.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for delivery recovery, artifact placement, result routing, checkpointing, and synthesis gates.

## Finish

Finish when the requested reconstruction is evidence-backed, required behavioral and project synthesis accepts, every Dispatch is accounted for, persistent mutations are verified, and material uncertainty is explicit.

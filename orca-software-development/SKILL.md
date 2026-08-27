---
name: orca-software-development
description: >-
  Use Orca for software work whose reasoning, scope, or parallelism justifies
  delegation: unknown-cause bugs, cross-module features or refactors,
  migrations, concurrency, substantial tests or reviews, independently
  verifiable workstreams, and explicit requests for Orca, Terra/Luna,
  parallel, or multi-agent execution. Let the primary coordinator agent
  directly complete a small localized edit when its location, behavior, patch
  scope, and focused validation are already clear. When delegating, send
  cohesive end-to-end Tasks with shared project context so workers do not
  repeat repository discovery.
metadata:
  version: "0.3.7"
---

# Orca Software Development

Complete development work with a user-facing primary coordinator, persistent Terra composer lanes, and high-throughput Luna leaf work. Correctness and required verification take precedence over usage.

## Establish the role

- With a live Orca Dispatch preamble and Task block, act only as that worker, follow the injected lifecycle, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as the primary coordinator. Own user interaction, design, input/output and behavior contracts, task boundaries, global decisions, and final project acceptance.
- Direct user instructions override inherited worker history. Never reuse settled lifecycle IDs.

A delegated Task is a closed authority envelope. Its objective and acceptance criteria do not authorize a worker to expand the stated lane, read/write scope, evidence budget, or decision authority. Scope is defined by the files, symbols, logs, commands, manifests, and behavior question explicitly supplied by the coordinator, not by everything transitively discovered while solving it. Stop the affected branch and return the applicable scope, bulk-evidence, or contract-decision request instead of widening the work independently.

## Choose the execution shape

- **Primary coordinator agent** — retain full capability, but default to design, behavioral validation, global supervision, and project review rather than ordinary coding or lifecycle narration. Directly finish a truly small localized change when delegation overhead would exceed the work.
- **Terra composer** — default owner of a cohesive semantic lane. Translate the accepted design into an integrated result, compose accepted Luna artifacts, and keep inspect -> implement -> test -> ordinary repair together. Reuse the same valid terminal for immediate continuation.
- **Luna leaf worker** — use freely for bounded work under stable inputs, interfaces, and acceptance: mechanical implementation, batch changes, tests, fixtures, validation, documentation, counterexample search, and result normalization.

Use the smallest reliable shape: direct coordinator, one Terra composer lane, or a multi-agent Run. Cheap Luna capacity does not justify per-file or per-test Tasks. Parallelize only independently acceptable work with stable interfaces and non-overlapping mutable state.

Read [references/decomposition.md](references/decomposition.md) whenever routing, lane boundaries, batching, or parallel safety is not obvious.

## Build context once

Pay broad repository discovery once per Run. Keep a compact Run Context plus one manifest per Terra lane: accepted design/contracts, relevant files and symbols, commands, accepted Luna artifacts, write boundaries, and unresolved questions. Pass references and deltas, not coordinator transcripts or repeated full discovery.

A Task owns one meaningful outcome and its complete local loop. Do not split exploration, implementation, tests, integration, or routine repair when they require the same mental model. Before creating any delegated Task, read [references/task-contracts.md](references/task-contracts.md) and persist its exact Luna or Terra model/effort profile in the Task.

## Run Orca safely

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Complete the delivery gate once: prove the intended Dispatch exists and the worker has begun processing; staged text without submission is not delivery. On a low-level terminal path, input and submit/Enter are one atomic delivery action—never yield the coordinator turn with the Task still in the worker's input box.

### Event-driven worker waiting — required

Before starting a new long Run-level wait—after the initial Dispatch wave, an actionable Delivery, or a true timeout—pause once for a bounded think-before-wait pass from accepted Run Context. Reconsider next steps, solution or research approach, remaining acceptance gaps, and useful coordinator-owned design or global reasoning. The pass may simply improve the plan, perform one bounded analysis, identify a stable independent Task worth dispatching, or conclude that waiting is correct; it need not produce new work. Do not repeat it for keepalive, command-runner yield, live-session resume, coordinator idleness, or ordinary completion of work selected by the same pass.

When the first Dispatch becomes active, choose one long Run-level liveness interval appropriate to the expected task duration and record it in the compact Run Context. It must normally be at least 15 minutes (`900000 ms`); longer intervals are encouraged for long tasks. Use that interval as the Orca lifecycle-wait timeout for all active workers.

Keep exactly one Run-level blocking wait in flight. A command-runner yield, keepalive, heartbeat, or coordinator idleness does not end it: resume the exact live process/session with the longest supported host wait, suppress transport-only frames with the live guide's supported filter when useful, and remain silent when it contains no lifecycle event. While that wait is alive, do not calculate, compare, or narrate elapsed time, remaining time, window fractions, deadline proximity, connection health, or worker/process health from transport or wait metadata. Tool-generated background-terminal records may remain visible; they are not coordinator work or a reason to comment. Do not issue another Orca command or status query while that wait is alive.

Carry the runtime reference's compact resume capsule across long waits and context compaction. Treat it as control state: compaction alone must not change the primary-coordinator role, accepted contracts, worker profiles, event filter, outstanding Dispatch accounting, delivery-gate status, consumed think-before-wait pass, or next legal action. In particular, it must not cause a new waiter, re-dispatch, another reflection pass, or status inspection.

Only an actionable Delivery, a true completed wait timeout, or an explicit wait failure/cancellation changes coordinator state. Process and acknowledge a Delivery under the live Orca contract. After a true timeout, perform at most one aggregate Run/task liveness check and start one new wait only if Dispatches remain outstanding. Follow exact runtime recovery for a failed wait without inferring worker failure. Do not poll individual workers unless aggregate state exposes a concrete anomaly, the user asks, or a material decision needs their output. This stricter policy narrows generic per-window liveness suggestions in the live guide; its Delivery, acknowledgement, and worker-accounting rules still apply.

Minimize primary-coordinator input at the source. Admit actionable lifecycle messages, compact decision evidence, and allowed aggregate checkpoints; filter transport frames, repeated receipts, routine status, and raw worker output before they enter coordinator context. Do not request routine worker heartbeats. When a live preamble or concrete reliability risk requires them, choose a long Run-level cadence and report phase changes rather than unchanged aliveness.

Reuse a warm Terra composer for same-lane continuation. Batch Luna work by independently acceptable outcome, locally accept low-risk results, and compact each completed wave before primary-coordinator review. The coordinator may inspect any underlying evidence when useful, while default user-facing output stays decision-focused.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for delivery recovery, placement, result routing, checkpointing, and review gates.

## Finish

Finish when acceptance criteria pass, required behavioral and project review accepts, every Dispatch is accounted for, and material risks are resolved.

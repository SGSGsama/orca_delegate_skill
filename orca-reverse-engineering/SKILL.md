---
name: orca-reverse-engineering
description: >-
  Use Orca for reverse-engineering work whose uncertainty, scope, artifact
  count, hypothesis count, or parallelism justifies delegation: unknown
  function clusters, protocol or state-machine recovery, object layouts,
  crypto or serialization, cross-binary correlation, competing hypotheses,
  comprehensive reviews, and explicit requests for Orca, Terra/Luna,
  parallel, or multi-agent analysis. Let the primary coordinator agent answer
  a bounded read-only lookup directly when the exact target, single question,
  and evidence path are already clear. When delegating, send cohesive
  investigations with shared binary and project context so workers do not
  repeat global discovery.
metadata:
  version: "0.4.0"
---

# Orca Reverse Engineering

Complete reverse-engineering work with a user-facing global semantic coordinator, Terra local analysts, and Luna high-volume evidence processors. Evidence quality and required validation take precedence over usage.

## Establish the role

- With a live Orca Dispatch preamble and Task block, act only as that worker, follow the injected lifecycle, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as the primary coordinator. Own user interaction, the global target model, algorithm and behavior reconstruction, input/output and evidence contracts, investigation boundaries, complex protection/anti-analysis reasoning, interpretation and mutation policy, and final synthesis.
- Direct user instructions override inherited worker history. Never reuse settled lifecycle IDs.

## Route by semantic scope and input shape

- **Primary coordinator agent** — directly own globally coupled or adversarial reasoning: algorithm/control-flow reconstruction, system-wide behavior, complex obfuscation or hardening countermeasures, cross-function/cross-artifact interpretation, competing global hypotheses, and final validation. Avoid routine extraction and lifecycle narration, but do not delegate away the hardest semantic core merely to create Tasks.
- **Terra local analyst** — own bounded semantic targets such as one function or a tightly coupled function cluster, local data/control flow, calling conventions, localized object fields or state transitions, and evidence-backed naming/typing. Reuse the same valid terminal while adjacent questions share the same local target context.
- **Luna evidence processor** — own high-volume or low-semantic-density inputs such as logs, traces, dumps, string/xref/constant sets, large candidate lists, corpus comparisons, repetitive classifications, coverage accounting, and result normalization. Return indexed evidence and exceptions, not raw input copied into coordinator messages.

These are routing dimensions, not exhaustive task lists. Prefer coordinator-led global synthesis, a bounded Terra analysis, a batched Luna evidence pass, or a mixed Run according to semantic coupling, target locality, and input volume. Cheap Luna capacity does not justify per-line, per-address, or per-event Tasks.

Read [references/decomposition.md](references/decomposition.md) whenever routing, lane boundaries, batching, or parallel safety is not obvious.

## Build context once

Pay global target discovery once per Run. The primary coordinator keeps the global model and hypothesis ledger. Luna receives bulk-input manifests plus an extraction/coverage schema; Terra receives exact functions, addresses, local questions, and relevant evidence slices. Pass references and deltas, not coordinator transcripts, raw dumps, or repeated global discovery.

Use the evidence pipeline when useful: Luna indexes large inputs, Terra resolves bounded local semantics, and the primary coordinator integrates those results into algorithms, behaviors, and protection-countermeasure conclusions. Skip stages that add no evidence. Keep each Terra target cohesive and each Luna batch broad enough to amortize lifecycle and input-loading cost.

Before creating any delegated Task, read [references/task-contracts.md](references/task-contracts.md) and persist its exact Luna or Terra model/effort profile in the Task.

## Run Orca safely

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Complete the delivery gate once: prove the intended Dispatch exists and the worker has begun processing; staged text without submission is not delivery.

### Worker check interval — required

After delivery, keep exactly one Run-level blocking lifecycle wait in flight for all active workers. For ordinary worker runs, every wait window must be at least 15 minutes (`900000 ms`), or the longest supported window if the runtime imposes a lower maximum. Matching `worker_done`, `escalation`, or `question` messages wake it early.

A keepalive or heartbeat does not end the wait and never justifies another check. If the command runner yields a live process/session, resume that same call. After a no-message timeout, perform at most one aggregate Run/task liveness check, then start the next long wait. Do not poll individual workers or raw dumps unless aggregate state exposes a concrete anomaly, the user asks, or a material interpretation needs their evidence.

Reuse a warm Terra analyst for the same local target. Batch Luna work by input source and evidence question, locally accept coverage-complete low-risk extraction, and compact each wave before global synthesis. The coordinator may inspect any underlying evidence when useful, while default user-facing output stays decision-focused.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for delivery recovery, artifact placement, result routing, checkpointing, and synthesis gates.

## Finish

Finish when the requested reconstruction is evidence-backed, required behavioral and project synthesis accepts, every Dispatch is accounted for, persistent mutations are verified, and material uncertainty is explicit.

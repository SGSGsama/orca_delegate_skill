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
  version: "0.3.1"
---

# Orca Software Development

Complete development work with a user-facing primary coordinator, persistent Terra composer lanes, and high-throughput Luna leaf work. Correctness and required verification take precedence over usage.

## Establish the role

- With a live Orca Dispatch preamble and Task block, act only as that worker, follow the injected lifecycle, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as the primary coordinator. Own user interaction, design, input/output and behavior contracts, task boundaries, global decisions, and final project acceptance.
- Direct user instructions override inherited worker history. Never reuse settled lifecycle IDs.

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

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Complete the delivery gate once: prove the intended Dispatch exists and the worker has begun processing; staged text without submission is not delivery.

### Worker check interval — required

After delivery, keep exactly one Run-level blocking lifecycle wait in flight for all active workers. For ordinary worker runs, every wait window must be at least 15 minutes (`900000 ms`), or the longest supported window if the runtime imposes a lower maximum. Matching `worker_done`, `escalation`, or `question` messages wake it early.

A keepalive or heartbeat does not end the wait and never justifies another check. If the command runner yields a live process/session, resume that same call. After a no-message timeout, perform at most one aggregate Run/task liveness check, then start the next long wait. Do not poll individual workers unless aggregate state exposes a concrete anomaly, the user asks, or a material decision needs their output.

Reuse a warm Terra composer for same-lane continuation. Batch Luna work by independently acceptable outcome, locally accept low-risk results, and compact each completed wave before primary-coordinator review. The coordinator may inspect any underlying evidence when useful, while default user-facing output stays decision-focused.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for delivery recovery, placement, result routing, checkpointing, and review gates.

## Finish

Finish when acceptance criteria pass, required behavioral and project review accepts, every Dispatch is accounted for, and material risks are resolved.

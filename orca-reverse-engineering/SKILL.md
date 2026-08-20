---
name: orca-reverse-engineering
description: >-
  Use Orca for reverse-engineering work whose scope, uncertainty, or
  parallelism justifies delegation: unknown function clusters, protocols,
  structures, multiple artifacts or hypotheses, and requests for
  comprehensive, parallel, multi-agent, or Orca analysis. Let the primary
  coordinator agent directly answer a bounded read-only lookup when the exact
  location, single question, and evidence path are already clear. When
  delegating, send cohesive investigations with shared binary and project
  context so workers do not repeat global discovery.
---

# Orca Reverse Engineering

Use Orca's structured orchestration for every delegated worker. Never substitute a generic subagent or chat-only spawn API, because it does not create Orca Task, Dispatch, lifecycle, or completion provenance.

## Establish the role

- If the current prompt contains a live Orca Dispatch preamble and Task block, act as a worker. Investigate only that bounded task, use the injected lifecycle commands, send `worker_done` exactly once, then end the dispatched turn. Do not create a nested orchestration tree.
- Otherwise act as the coordinator. Own the global model, task decomposition, synthesis, disputed conclusions, accepted naming/types, and final answer.
- A direct user instruction always takes precedence over an inherited worker role. Do not reuse lifecycle IDs from a settled Dispatch.

## Decide whether the primary coordinator agent should analyze directly

Before creating a Run, the primary coordinator agent may inspect target metadata, perform up to three targeted symbol/string/address searches, and open the named function plus its immediate references. Use that bounded reconnaissance to choose one path.

Use the **primary-coordinator fast path** only when all six conditions hold:

1. the request asks one precise semantic or factual question;
2. the exact binary, function, address, symbol, or artifact is already known or found by the bounded reconnaissance;
3. the evidence is confined to one function/artifact and its immediate callers, callees, or xrefs;
4. no competing hypothesis, protocol/state-machine recovery, object-layout inference, crypto/serialization reconstruction, or cross-artifact correlation is required;
5. the work is read-only and needs no broad naming, typing, annotation, or documentation propagation;
6. there is no independent investigation whose delegation benefit exceeds the context-preparation and launch cost.

When all six hold, the primary coordinator agent answers the lookup directly. Delegate when any condition fails, the target remains uncertain, or the question expands beyond the bounded evidence path. Convert the reconnaissance results into the shared context packet instead of making every worker rediscover them.

An explicit user request for Orca, Terra/Luna, parallel work, multi-agent supervision, or comprehensive investigation overrides the fast path and requires delegation.

## Load the current Orca contract

Before the first Orca command, read the installed `orca-cli` and `orchestration` skills. Resolve the executable exactly as they specify, then run the version-matched guide. `<ORCA_CLI>` below is a documentation placeholder: substitute the resolved executable in every command; do not create a shell variable or run the placeholder literally.

```text
<ORCA_CLI> skills get orchestration
```

Treat that live guide as authoritative if any command below has changed. Do not guess flags. Confirm the runtime with `<ORCA_CLI> status --json`; follow the guide's startup action if it is not running. If the selected executable fails, report its exact error and stop rather than trying a different executable.

## Coordinator model

The primary coordinator agent keeps the compact, global understanding. Do not restart or replace an existing coordinator merely to change its model.

- objective and subsystem boundaries
- accepted facts versus hypotheses
- cross-function control and data flow
- structures, state, protocols, and algorithms
- contradictions, confidence, and evidence gaps
- the next highest-value investigation

On the primary-coordinator fast path, inspect the bounded evidence directly. On the delegated path, keep raw pseudocode, disassembly, traces, and repetitive inspection in workers unless exact evidence is needed to settle a claim.

## Route work

Use `gpt-5.6-terra` with `max` effort for genuine unknown-code reasoning: ambiguous functions, data flow, object layouts, local state machines, parsers, crypto, serialization, optimized code, indirect calls, or hypothesis testing.

Use `gpt-5.6-luna` with `max` effort only after the analytical pattern is constrained: wrappers and thunks, repetitive classification, extracting constants/xrefs, applying an accepted structure, propagating names/types/comments, or updating documentation.

Keep cross-subsystem synthesis, whole-protocol reconstruction, conflict resolution, and acceptance with the coordinator. Detailed local evidence recovery belongs to workers once the mandatory delegation gate is met.

## Persist model and effort across long runs

Treat the worker profile as part of the Task contract, not coordinator memory. Every Task spec must begin with exactly one of these lines:

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
```

Choose one line, never both. Keeping it first makes the profile visible in brief task listings after long waits or context compaction.

Before every initial launch, capacity-refill launch, replacement, or retry:

1. recover the profile from the persisted Task spec rather than memory;
2. for a fresh terminal, pass both the exact `--model` and `--effort` values to `worker-start`;
3. inspect the returned receipt and require `launch.requested` and `launch.effective` to match the Task profile;
4. if the profile is unsupported or mismatched, treat the launch as failed and follow its typed recovery guidance; never retry by omitting or lowering effort.

`--retry-of` does not inherit the prior profile, so repeat the exact model and effort explicitly. Reuse with `worker-start --terminal` only when the previous Dispatch receipt proves that exact terminal already has the same effective model and effort; model and effort flags cannot be combined with `--terminal`. If the next Task needs a different profile, release the terminal and start a fresh worker.

After a timeout, long worker run, context compaction, coordinator restart, or resumed orchestration loop, re-read Task specs and active Dispatch receipts before launching more work. Never silently fall back to agent defaults.

## Build bounded tasks

Inspect enough of the target to identify separable functions, regions, or hypotheses. A task must name its scope and ask falsifiable questions. Include available artifacts, relevant callers/callees, known facts, current hypotheses, allowed mutations, expected evidence, and output format.

Read [references/task-templates.md](references/task-templates.md) when drafting a function, structure, protocol, contradiction-resolution, or propagation task.

Create all independent Tasks before starting their workers so they can run as one parallel wave. Use dependencies for real ordering constraints. Avoid two workers mutating the same analysis database or output file unless independent verification is intentional and writes are disabled. Do not split local discovery, hypothesis testing, evidence collection, and conclusions into separate Tasks when they repeatedly require the same function cluster and artifacts.

## Favor broad, useful fan-out

For every candidate workstream, apply this three-part test:

1. **Clear boundary:** the function cluster, subsystem, artifact, or hypothesis can be investigated without another worker continuously changing its meaning.
2. **Cohesive objective:** the Task owns a meaningful analytical result, not a tiny instruction such as reading one xref or renaming one variable.
3. **Portable context:** the Task spec and bounded artifacts contain enough local facts for the worker to perform at full quality without carrying the coordinator's entire global history.

When all three hold, strongly prefer more dispatches over keeping ready analysis in the coordinator or serializing it behind an unrelated worker. Create and start every ready Task before the first wait, use the available safe concurrency, and dispatch the next ready Task as capacity returns. Several workers may use the same model when their scopes are genuinely independent.

Good fan-out boundaries include independent function clusters, receive/send/dispatch paths, unrelated message families, separate binaries or artifacts, and competing hypotheses evaluated read-only. Bundle tightly coupled steps into one larger Task when they repeatedly need the same local state.

Stop widening the wave when a proposed split would create micro-tasks, require lossy or very large context transfer, introduce a real dependency on unfinished findings, duplicate most of another worker's analysis, create overlapping mutations, or cost as much context preparation as direct analysis. Coordinator bookkeeping alone is not a reason to avoid otherwise useful fan-out.

## Build and reuse shared reverse-engineering context

Pay global discovery cost once per Run. Before dispatching detailed investigations, create a compact shared context packet containing:

- the global question, target identities, formats, architecture, and tool/database locations;
- accepted subsystem boundaries, call paths, known structures, state, constants, and naming decisions;
- important entry points, xrefs, traces, strings, captures, and already-tested hypotheses;
- mutation ownership, writable artifacts, and conclusions that remain provisional;
- the exact commands or tool views workers should use to reach the local evidence.

Keep it focused on facts workers would otherwise have to rediscover. Prefer an inline packet for remote or uncertain placement. A shared report path is acceptable only when every target worker is proven to share that filesystem; include a short inline fallback summary even then.

Every Task must include the shared packet or reference, exact local starting points, and the delta question it owns. Workers should accept coordinator-approved facts, inspect only task-local unknowns, and report contradictions rather than repeating global reconnaissance. Update the packet after each synthesis wave before creating later Tasks.

If the primary coordinator agent cannot build a reliable packet within the bounded reconnaissance, dispatch one read-only Terra scout Task to map the relevant binaries, functions, call paths, artifacts, and tool entry points. Synthesize that result into the packet before launching detailed workers; do not launch several workers to repeat the same global discovery.

Make a Task an end-to-end context unit: local exploration, hypothesis testing, evidence collection, and conclusion belong to the same worker when they use the same function cluster or artifacts. Keep its Dispatch active for multi-round `send` and `ask/reply`; do not request `worker_done` until that cohesive investigation is complete. If an immediate follow-up uses the same context and the same verified worker profile, reuse the exact terminal. Start a fresh worker only for an independent context unit, a different required profile, or a settled worker that cannot be safely reused.

## Run the supervised Orca loop

Create one Run for the objective, unless the session is already bound to the correct live Run:

```text
<ORCA_CLI> orchestration run-create --objective "<global reverse-engineering objective>" --json
<ORCA_CLI> orchestration task-create --spec "[worker-profile: agent=codex model=gpt-5.6-terra effort=max] <bounded investigation spec>" --json
```

Start workers with the preferred composed path and retain the returned Task and Dispatch IDs:

```text
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-terra --effort max --json
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-luna --effort max --json
```

Use the command matching the Task's persisted profile and verify the launch receipt before counting the worker as started.

`current` means a fresh agent terminal in the current worktree. Use an exact existing worktree when artifacts live elsewhere. Create a new worktree only when the user requests one or a concrete checkout/filesystem conflict makes sharing impossible; state that conflict before creation and follow the live guide's lineage, base, and setup rules.

Verify provenance when needed:

```text
<ORCA_CLI> orchestration task-list --json
<ORCA_CLI> orchestration dispatch-show --task <task_id> --json
```

Wait for structured lifecycle messages, not a fixed number of batches:

```text
<ORCA_CLI> orchestration check --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

Process every message in the returned Delivery. Answer worker questions with `orchestration reply --id <message_id> --body "<answer>" --json`. While a cohesive Task is active, send clarifications to `dispatch:<dispatch_id>` instead of creating another Task for the next conversational turn. A timeout is only a checkpoint; if the Dispatch is still live, continue rolling waits. Use bounded `worker-show` or `worker-read` only when liveness or evidence needs inspection. Do not infer completion from terminal idleness or heartbeat.

For every accepted `worker_done`, inspect the finding and choose one before acknowledging the Delivery:

- immediately reuse the exact terminal for a follow-up Task with `worker-start --terminal <handle>`; or
- run `worker-release --dispatch <dispatch_id> --json`.

Use `worker-retain` only when the user explicitly wants the completed worker kept live. Follow typed recovery guidance for failed, stopped, unknown, or pending-release Dispatches; do not close terminals manually. A valid `worker_done` settles the Task automatically, so do not also mark it completed.

After processing the entire Delivery and accounting for settled workers, acknowledge it and continue waiting while any expected Dispatch remains:

```text
<ORCA_CLI> orchestration check --ack <delivery_id> --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

## Synthesize each wave

After each useful batch, update the coordinator's compact ledger:

- accepted conclusion and scope
- supporting evidence and source location
- confidence and alternatives
- contradictions or missing evidence
- accepted names, types, and offsets
- next investigation or safe propagation

Do not accumulate worker summaries without integration. If workers disagree, isolate the exact disputed claim, compare their evidence, and dispatch a narrower Terra task designed to distinguish the hypotheses. The coordinator decides what becomes accepted.

Only after acceptance, dispatch Luna propagation tasks with an explicit mapping and writable scope. If propagation uncovers contradictory evidence, stop the mutation, downgrade the conclusion to a hypothesis, and return it to Terra/coordinator review.

## Worker completion contract

Return concise findings rather than raw dumps. Include conclusion, evidence with addresses/functions/artifact paths, confidence, contradictions, side effects or mutations, and recommended follow-up. Use the exact `worker_done` command and IDs injected by Orca, with explicit `--outcome succeeded` or `--outcome failed` and accurate modified-file reporting.

## Finish

On the fast path, report the bounded answer and its evidence. On the delegated path, account for every Dispatch, verify any persistent analysis-database or documentation mutations, and present the global reconstruction separately from unresolved hypotheses. Do not claim a worker was Orca-orchestrated unless its Task and Dispatch exist.

---
name: orca-reverse-engineering
description: Use Orca by default for reverse-engineering requests involving unknown compiled code, binaries, APKs or native libraries, multiple functions, protocols, data structures, decompiler output, or evidence cross-checking. Trigger whenever there are two or more separable analysis questions or targets, the scope is initially unknown, or the user asks for comprehensive, parallel, multi-agent, or Orca analysis. A coordinator must delegate bounded investigation to Terra or Luna, favor broad safe fan-out when modules and context permit, and synthesize the evidence. Exclude only a single trivial read-only lookup requiring no broader code exploration.
---

# Orca Reverse Engineering

Use Orca's structured orchestration for every delegated worker. Never substitute a generic subagent or chat-only spawn API, because it does not create Orca Task, Dispatch, lifecycle, or completion provenance.

## Establish the role

- If the current prompt contains a live Orca Dispatch preamble and Task block, act as a worker. Investigate only that bounded task, use the injected lifecycle commands, send `worker_done` exactly once, then end the dispatched turn. Do not create a nested orchestration tree.
- Otherwise act as the coordinator. Own the global model, task decomposition, synthesis, disputed conclusions, accepted naming/types, and final answer.
- A direct user instruction always takes precedence over an inherited worker role. Do not reuse lifecycle IDs from a settled Dispatch.

## Mandatory delegation gate

When this skill is selected in coordinator mode, delegation is the default action, not an optional optimization. Inspect only enough raw material to identify boundaries and write the first Task; then create the Run and start at least one Orca worker before doing detailed function analysis, protocol reconstruction, bulk xref review, renaming, typing, or analysis-database mutation.

Delegation is mandatory when any of these is true:

- the request contains two or more functions, artifacts, hypotheses, or independent questions;
- the scope or root behavior is not yet known;
- the work combines discovery with propagation, documentation, or verification;
- the user asks for a thorough, comprehensive, parallel, multi-agent, Terra/Luna, or Orca investigation.

Coordinator-only execution is allowed only when all of these are true: the request names one exact fact or location, is read-only, has one obvious inspection operation, and needs no caller/callee or cross-artifact exploration. If uncertain, delegate. The coordinator's ability to perform the analysis itself is not a reason to skip Orca.

## Load the current Orca contract

Before the first Orca command, read the installed `orca-cli` and `orchestration` skills. Resolve the executable exactly as they specify, then run the version-matched guide. `<ORCA_CLI>` below is a documentation placeholder: substitute the resolved executable in every command; do not create a shell variable or run the placeholder literally.

```text
<ORCA_CLI> skills get orchestration
```

Treat that live guide as authoritative if any command below has changed. Do not guess flags. Confirm the runtime with `<ORCA_CLI> status --json`; follow the guide's startup action if it is not running. If the selected executable fails, report its exact error and stop rather than trying a different executable.

## Coordinator model

The coordinator (typically Sol when the workflow is launched with a model choice) keeps the compact, global understanding. Do not restart or replace an existing coordinator merely to change its model.

- objective and subsystem boundaries
- accepted facts versus hypotheses
- cross-function control and data flow
- structures, state, protocols, and algorithms
- contradictions, confidence, and evidence gaps
- the next highest-value investigation

Keep raw pseudocode, disassembly, traces, and repetitive inspection in workers unless exact evidence is needed to settle a claim.

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

Create all independent Tasks before starting their workers so they can run as one parallel wave. Use dependencies for real ordering constraints. Avoid two workers mutating the same analysis database or output file unless independent verification is intentional and writes are disabled.

## Favor broad, useful fan-out

For every candidate workstream, apply this three-part test:

1. **Clear boundary:** the function cluster, subsystem, artifact, or hypothesis can be investigated without another worker continuously changing its meaning.
2. **Cohesive objective:** the Task owns a meaningful analytical result, not a tiny instruction such as reading one xref or renaming one variable.
3. **Portable context:** the Task spec and bounded artifacts contain enough local facts for the worker to perform at full quality without carrying the coordinator's entire global history.

When all three hold, strongly prefer more dispatches over keeping ready analysis in the coordinator or serializing it behind an unrelated worker. Create and start every ready Task before the first wait, use the available safe concurrency, and dispatch the next ready Task as capacity returns. Several workers may use the same model when their scopes are genuinely independent.

Good fan-out boundaries include independent function clusters, receive/send/dispatch paths, unrelated message families, separate binaries or artifacts, and competing hypotheses evaluated read-only. Bundle tightly coupled steps into one larger Task when they repeatedly need the same local state.

Stop widening the wave when a proposed split would create micro-tasks, require lossy or very large context transfer, introduce a real dependency on unfinished findings, duplicate most of another worker's analysis, or create overlapping mutations. Coordinator bookkeeping alone is not a reason to avoid otherwise useful fan-out.

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

Process every message in the returned Delivery. Answer worker questions with `orchestration reply --id <message_id> --body "<answer>" --json`. A timeout is only a checkpoint; if the Dispatch is still live, continue rolling waits. Use bounded `worker-show` or `worker-read` only when liveness or evidence needs inspection. Do not infer completion from terminal idleness or heartbeat.

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

Account for every Dispatch, verify any persistent analysis-database or documentation mutations, and present the global reconstruction separately from unresolved hypotheses. Do not claim a worker was Orca-orchestrated unless its Task and Dispatch exist.

---
name: orca-software-development
description: >-
  Use Orca for software work whose reasoning, scope, or parallelism justifies
  delegation: unknown-cause bugs, cross-module features or refactors,
  substantial tests or reviews, and requests for parallel, multi-agent,
  Terra/Luna, or Orca execution. Let the primary coordinator agent directly
  complete a small localized edit when its location, behavior, patch scope,
  and focused validation are already clear. When delegating, send cohesive
  end-to-end Tasks with shared project context so workers do not rediscover
  the repository.
---

# Orca Software Development

Use Orca's structured orchestration for every delegated worker. Never substitute a generic subagent or chat-only spawn API, because it does not create Orca Task, Dispatch, lifecycle, or completion provenance.

## Establish the role

- If the current prompt contains a live Orca Dispatch preamble and Task block, act as a worker. Implement only that bounded contract, use the injected lifecycle commands, send `worker_done` exactly once, then end the dispatched turn. Do not create a nested orchestration tree.
- Otherwise act as the coordinator. Own requirements, architecture, task boundaries, integration, review, and final acceptance.
- A direct user instruction always takes precedence over an inherited worker role. Do not reuse lifecycle IDs from a settled Dispatch.

## Decide whether the primary coordinator agent should edit directly

Before creating a Run, the primary coordinator agent may read repository instructions, perform up to three targeted searches, open the directly implicated files, and reproduce one focused failure. Use that bounded reconnaissance to choose one path.

Use the **primary-coordinator fast path** only when all six conditions hold:

1. the requested behavior and acceptance result are unambiguous;
2. the edit location is already known or found by the bounded reconnaissance;
3. the expected patch is localized to one cohesive file, or at most two tightly coupled files, and 40 changed lines or fewer excluding generated/formatting churn;
4. no root-cause discovery, public API/schema change, new dependency, data-model migration, concurrency redesign, or security-sensitive reasoning is required;
5. one targeted test or validation command can establish completion;
6. there is no independent workstream whose delegation benefit exceeds the cost of preparing context and launching a worker.

When all six hold, the primary coordinator agent owns the complete inspect-edit-validate loop and does not delegate. Typical examples are a typo or constant correction, one local guard, a narrowly specified configuration change, or updating one implementation and its tightly coupled expectation.

Delegate when any condition fails, the bounded reconnaissance does not locate the change, or the work expands beyond the estimate. Stop the fast path before broad edits and convert the discovered facts into the shared context packet. Typical delegated work includes unknown-cause failures, cross-module behavior, new interfaces, migrations, concurrency, broad refactors, and multiple genuinely independent deliverables.

An explicit user request for Orca, Terra/Luna, parallel work, or multi-agent supervision overrides the fast path and requires delegation.

## Load the current Orca contract

Before the first Orca command, read the installed `orca-cli` and `orchestration` skills. Resolve the executable exactly as they specify, then run the version-matched guide. `<ORCA_CLI>` below is a documentation placeholder: substitute the resolved executable in every command; do not create a shell variable or run the placeholder literally.

```text
<ORCA_CLI> skills get orchestration
```

Treat that live guide as authoritative if any command below has changed. Do not guess flags. Confirm the runtime with `<ORCA_CLI> status --json`; follow the guide's startup action if it is not running. If the selected executable fails, report its exact error and stop rather than trying a different executable.

## Coordinator model

The primary coordinator agent first inspects repository instructions and the relevant code, then owns the items below. Do not restart or replace an existing coordinator merely to change its model.

- requirement interpretation and acceptance criteria
- architecture, public APIs, cross-module contracts, and data model
- global concurrency model and important invariants
- task dependency and writable-scope boundaries
- review, integration, test strategy, and final acceptance

On the primary-coordinator fast path, the coordinator owns the complete edit. On the delegated path, the coordinator inspects, specifies, schedules, reviews, and integrates while workers own routine implementation and local debugging.

## Route work

Use `gpt-5.6-luna` with `max` effort when the contract is precise and execution is mostly mechanical: defined interfaces, adapters, serializers, validation rules, fixtures, tests, boilerplate, repetitive refactors, or a straightforward fix whose cause is known.

Use `gpt-5.6-terra` with `xhigh` effort when a bounded task still needs substantial local reasoning: unknown bug causes, concurrency, nontrivial algorithms, complex state machines, difficult legacy code, performance diagnosis, unclear behavior, or hard test failures.

Keep global architecture, public API design, cross-module contracts, major data-model changes, global concurrency decisions, conflicts between findings, and final acceptance with the coordinator. If those decisions are unresolved, investigate first instead of dispatching an underspecified implementation.

## Persist model and effort across long runs

Treat the worker profile as part of the Task contract, not coordinator memory. Every Task spec must begin with exactly one of these lines:

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
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

Create tasks whose contracts a worker can verify independently. Include files/directories in scope, behavior, interfaces allowed or forbidden to change, invariants, error behavior, compatibility constraints, acceptance criteria, and exact validation commands. Record whether the task is implementation, diagnosis-only, tests-only, review-only, or documentation.

Read [references/task-templates.md](references/task-templates.md) when drafting implementation, diagnosis, test, review, or repair tasks.

Create every independent Task before starting workers so one parallel wave can start before waiting. Add dependencies for actual ordering constraints. Parallel tasks must have non-overlapping writable scopes, or be explicitly read-only. Do not split local exploration, implementation, tests, and ordinary repair into separate Tasks when one worker needs the same context for the entire loop.

## Favor broad, useful fan-out

For every candidate workstream, apply this three-part test:

1. **Clear boundary:** the module, component, file ownership, or read-only investigation scope has a stable interface to the rest of the change.
2. **Cohesive objective:** the Task owns a meaningful deliverable with its own acceptance criteria, not a tiny implementation fragment or isolated command.
3. **Portable context:** repository instructions, relevant contracts, and bounded code context can be included without omitting global decisions that materially affect worker quality.

When all three hold, strongly prefer more dispatches over keeping ready implementation or diagnosis in the coordinator or serializing it behind unrelated work. Create and start every ready Task before the first wait, use the available safe concurrency, and dispatch the next ready Task as capacity returns. Several workers may use the same model when their scopes are genuinely independent.

Good fan-out boundaries include separate modules with stable interfaces, independent adapters, unrelated bug investigations, distinct migration batches, read-only review surfaces, and tests whose writable scope does not overlap implementation. Bundle implementation and tests into one Task when they require repeated edits to the same core files or rapid shared feedback.

Stop widening the wave when a proposed split would create micro-tasks, require lossy or very large context transfer, depend on an unfinished contract or design decision, duplicate most of another worker's work, introduce overlapping writes, or cost as much context preparation as doing the work directly. Coordinator bookkeeping alone is not a reason to avoid otherwise useful fan-out.

## Build and reuse shared project context

Pay repository-discovery cost once per Run. Before dispatching implementation workers, create a compact shared context packet containing:

- the user objective and accepted architecture or API decisions;
- applicable repository instructions and important user-owned uncommitted changes;
- a small module map naming relevant files, symbols, interfaces, and dependencies;
- established facts, rejected assumptions, writable boundaries, and forbidden changes;
- exact build, test, lint, or reproduction commands already discovered.

Keep it focused on decisions workers would otherwise have to rediscover. Prefer an inline packet in each Task spec for remote or uncertain placement. A shared report path is acceptable only when every target worker is proven to share that filesystem; include a short inline fallback summary even then.

Every Task must include the shared packet or reference, plus exact local starting points. Workers should trust accepted decisions, inspect only task-local unknowns, and avoid broad repository exploration unless they find contradictory evidence. After each wave, update the packet with accepted findings before creating later Tasks.

If the primary coordinator agent cannot build a reliable packet within the bounded reconnaissance, dispatch one read-only Terra scout Task to map the relevant modules, contracts, tests, and commands. Synthesize that result into the packet before launching implementation workers; do not launch several workers to repeat the same global discovery.

Make a Task an end-to-end context unit: local inspection, implementation, targeted tests, and ordinary repair belong to the same worker when they touch the same module and decisions. Keep its Dispatch active for multi-round `send` and `ask/reply`; do not request `worker_done` until that cohesive objective is complete. If an immediate follow-up uses the same context and the same verified worker profile, reuse the exact terminal. Start a fresh worker only for an independent context unit, a different required profile, or a settled worker that cannot be safely reused.

## Choose placement

Default to a fresh agent terminal in the current worktree. This preserves uncommitted state and does not imply that workers share one agent session.

Use an exact existing worktree when required. Create a new worktree only when the user explicitly requests one or a concrete checkout/filesystem conflict makes shared placement unsafe or impossible. State the conflict before creation and follow the live guide's lineage, Git base, and `--setup run` rules. Parallelism alone is not a reason to create worktrees.

## Run the supervised Orca loop

Create one Run for the objective, unless the session is already bound to the correct live Run:

```text
<ORCA_CLI> orchestration run-create --objective "<global development objective>" --json
<ORCA_CLI> orchestration task-create --spec "[worker-profile: agent=codex model=gpt-5.6-luna effort=max] <bounded worker contract>" --json
```

Start workers with the preferred composed path and retain the returned Task and Dispatch IDs:

```text
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-luna --effort max --json
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-terra --effort xhigh --json
```

Use the command matching the Task's persisted profile and verify the launch receipt before counting the worker as started.

Verify provenance when needed:

```text
<ORCA_CLI> orchestration task-list --json
<ORCA_CLI> orchestration dispatch-show --task <task_id> --json
```

Wait for lifecycle messages rather than continuously reading terminals:

```text
<ORCA_CLI> orchestration check --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

Process every message in the returned Delivery. Answer worker questions with `orchestration reply --id <message_id> --body "<answer>" --json`. While a cohesive Task is active, send clarifications to `dispatch:<dispatch_id>` instead of creating another Task for the next conversational turn. A timeout is only a checkpoint; if the Dispatch is live, continue rolling waits. Use bounded `worker-show` or `worker-read` only to inspect liveness or evidence. Do not infer completion from TUI idleness or heartbeat.

For every accepted `worker_done`, inspect the result and choose one before acknowledging the Delivery:

- immediately reuse the exact terminal for a follow-up Task with `worker-start --terminal <handle>`; or
- run `worker-release --dispatch <dispatch_id> --json`.

Use `worker-retain` only when the user explicitly wants the completed worker kept live. Follow typed recovery guidance for failed, stopped, unknown, or pending-release Dispatches; do not close terminals manually. A valid `worker_done` settles the Task automatically, so do not also mark it completed.

After processing the entire Delivery and accounting for settled workers, acknowledge it and continue waiting while any expected Dispatch remains:

```text
<ORCA_CLI> orchestration check --ack <delivery_id> --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

## Review and integrate

Worker completion is evidence, not acceptance. After each result:

1. compare the diff and behavior with the task contract;
2. inspect changed interfaces, error paths, and unrelated edits;
3. run or independently verify the relevant tests, type checks, linters, or benchmarks;
4. check interactions with other worker changes and repository-wide invariants;
5. accept, dispatch a narrow repair, or redesign at coordinator level.

Route a known mechanical repair to Luna. Route diagnosis or difficult local reasoning to Terra. If the architecture or contract is wrong, the coordinator revises it before dispatching more implementation.

Respect existing user changes in shared worktrees. Do not overwrite or revert unrelated modifications. If two completed branches/worktrees require integration, inspect both diffs and merge according to the repository's normal workflow; worker completion does not authorize an external PR, push, or deployment unless the user requested it.

## Worker completion contract

Workers perform their own exploration, edit/test loop, and local debugging. They escalate only coordinator-owned decisions or invalid task assumptions. The final report should name changed files, behavior implemented or diagnosed, validation commands and results, remaining risks, and any deviation from scope.

Use the exact `worker_done` command and IDs injected by Orca, with explicit `--outcome succeeded` or `--outcome failed` and accurate `--files-modified`. A review-only completion reports findings and does not authorize coordinator file edits unless the user assigned those edits to the coordinator.

## Finish

On the fast path, run the focused validation and report the local change. On the delegated path, account for every Dispatch, run final integration validation, and report the accepted outcome plus any unresolved risks. Do not claim a worker was Orca-orchestrated unless its Task and Dispatch exist.

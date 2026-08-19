---
name: orca-software-development
description: Use Orca by default for non-trivial software work, including feature implementation, bug diagnosis or fixes, refactoring, tests, reviews, and multi-file or multi-component changes. Trigger whenever work needs repository exploration plus code changes, contains two or more separable steps or concerns, has an unknown cause, or needs both implementation and verification; also trigger on requests for parallel, multi-agent, Terra/Luna, or Orca execution. A coordinator must delegate bounded execution and retain design, review, and acceptance. Exclude only a single obvious local edit or a read-only explanation.
---

# Orca Software Development

Use Orca's structured orchestration for every delegated worker. Never substitute a generic subagent or chat-only spawn API, because it does not create Orca Task, Dispatch, lifecycle, or completion provenance.

## Establish the role

- If the current prompt contains a live Orca Dispatch preamble and Task block, act as a worker. Implement only that bounded contract, use the injected lifecycle commands, send `worker_done` exactly once, then end the dispatched turn. Do not create a nested orchestration tree.
- Otherwise act as the coordinator. Own requirements, architecture, task boundaries, integration, review, and final acceptance.
- A direct user instruction always takes precedence over an inherited worker role. Do not reuse lifecycle IDs from a settled Dispatch.

## Mandatory delegation gate

When this skill is selected in coordinator mode, the coordinator must delegate implementation and diagnosis through Orca. It may inspect repository instructions and enough code to define contracts, but it must create the Run and start at least one worker before editing production or test code.

Delegation is mandatory when any of these is true:

- more than one file, component, behavior, or verification concern may be affected;
- the root cause or implementation approach requires exploration;
- the request is a feature, non-local bug fix, refactor, test-and-implementation change, or code review followed by repair;
- meaningful implementation, testing, review, or documentation tasks can be separated;
- the user asks for thorough, parallel, multi-agent, Terra/Luna, or Orca execution.

Coordinator-only implementation is allowed only when all of these are true: one already-identified file, one obvious local change, no debugging or design decision, no public interface or behavioral ambiguity, and one direct validation command. If uncertain, delegate. Once this skill has triggered, the coordinator does not write routine implementation code merely because it can; even small review repairs go to a narrow Luna Task unless the user explicitly asks the coordinator to edit them.

## Load the current Orca contract

Before the first Orca command, read the installed `orca-cli` and `orchestration` skills. Resolve the executable exactly as they specify, then run the version-matched guide. `<ORCA_CLI>` below is a documentation placeholder: substitute the resolved executable in every command; do not create a shell variable or run the placeholder literally.

```text
<ORCA_CLI> skills get orchestration
```

Treat that live guide as authoritative if any command below has changed. Do not guess flags. Confirm the runtime with `<ORCA_CLI> status --json`; follow the guide's startup action if it is not running. If the selected executable fails, report its exact error and stop rather than trying a different executable.

## Coordinator model

The coordinator (typically Sol when the workflow is launched with a model choice) first inspects repository instructions and the relevant code, then owns the items below. Do not restart or replace an existing coordinator merely to change its model.

- requirement interpretation and acceptance criteria
- architecture, public APIs, cross-module contracts, and data model
- global concurrency model and important invariants
- task dependency and writable-scope boundaries
- review, integration, test strategy, and final acceptance

Keep routine implementation and local debugging in bounded workers. The coordinator inspects, specifies, schedules, reviews, and integrates; workers own code edits.

## Route work

Use `gpt-5.6-luna` with `max` effort when the contract is precise and execution is mostly mechanical: defined interfaces, adapters, serializers, validation rules, fixtures, tests, boilerplate, repetitive refactors, or a straightforward fix whose cause is known.

Use `gpt-5.6-terra` with `xhigh` effort when a bounded task still needs substantial local reasoning: unknown bug causes, concurrency, nontrivial algorithms, complex state machines, difficult legacy code, performance diagnosis, unclear behavior, or hard test failures.

Keep global architecture, public API design, cross-module contracts, major data-model changes, global concurrency decisions, conflicts between findings, and final acceptance with the coordinator. If those decisions are unresolved, investigate first instead of dispatching an underspecified implementation.

## Build bounded tasks

Create tasks whose contracts a worker can verify independently. Include files/directories in scope, behavior, interfaces allowed or forbidden to change, invariants, error behavior, compatibility constraints, acceptance criteria, and exact validation commands. Record whether the task is implementation, diagnosis-only, tests-only, review-only, or documentation.

Read [references/task-templates.md](references/task-templates.md) when drafting implementation, diagnosis, test, review, or repair tasks.

Create every independent Task before starting workers so one parallel wave can start before waiting. Add dependencies for actual ordering constraints. Parallel tasks must have non-overlapping writable scopes, or be explicitly read-only. Do not send implementation and tests to separate workers when both must repeatedly edit the same core files.

## Choose placement

Default to a fresh agent terminal in the current worktree. This preserves uncommitted state and does not imply that workers share one agent session.

Use an exact existing worktree when required. Create a new worktree only when the user explicitly requests one or a concrete checkout/filesystem conflict makes shared placement unsafe or impossible. State the conflict before creation and follow the live guide's lineage, Git base, and `--setup run` rules. Parallelism alone is not a reason to create worktrees.

## Run the supervised Orca loop

Create one Run for the objective, unless the session is already bound to the correct live Run:

```text
<ORCA_CLI> orchestration run-create --objective "<global development objective>" --json
<ORCA_CLI> orchestration task-create --spec "<bounded worker contract>" --json
```

Start workers with the preferred composed path and retain the returned Task and Dispatch IDs:

```text
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-luna --effort max --json
<ORCA_CLI> orchestration worker-start --task <task_id> --worktree current --agent codex --model gpt-5.6-terra --effort xhigh --json
```

Verify provenance when needed:

```text
<ORCA_CLI> orchestration task-list --json
<ORCA_CLI> orchestration dispatch-show --task <task_id> --json
```

Wait for lifecycle messages rather than continuously reading terminals:

```text
<ORCA_CLI> orchestration check --wait --types worker_done,escalation,question --timeout-ms 900000 --json
```

Process every message in the returned Delivery. Answer worker questions with `orchestration reply --id <message_id> --body "<answer>" --json`. A timeout is only a checkpoint; if the Dispatch is live, continue rolling waits. Use bounded `worker-show` or `worker-read` only to inspect liveness or evidence. Do not infer completion from TUI idleness or heartbeat.

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

Account for every Dispatch, run final integration validation, and report the accepted outcome plus any unresolved risks. Do not claim a worker was Orca-orchestrated unless its Task and Dispatch exist.

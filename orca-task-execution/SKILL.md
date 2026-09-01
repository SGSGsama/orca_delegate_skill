---
name: orca-task-execution
description: >-
  Use Orca to choose and enforce execution ownership for non-trivial software
  development, reverse engineering, or mixed work that benefits from
  Terra/Luna delegation. Classify work by deliverable, choose direct or
  delegated execution, then load only the selected domain and role contract.
  This skill is the sole authority for primary/Terra/Luna ownership and worker
  profiles; tool, testing, and analysis skills constrain execution method but
  never assign ownership. Direct work is limited to bounded tasks and must be
  re-routed when scope expands.
metadata:
  version: "1.0.1"
---

# Orca Task Execution

Route software-development and reverse-engineering work through one execution-ownership contract while loading only the domain and worker instructions required by the current Task.

## Establish authority

- With a live Orca Dispatch preamble and Task block, act only as that worker, stay inside the injected contract, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as the primary coordinator. Own user interaction, task classification, execution shape, contracts, scope changes, global decisions, and final acceptance.
- Direct user instructions override inherited worker history. Never reuse settled lifecycle IDs.

`$orca-task-execution` is the sole authority for direct/primary/Terra/Luna ownership, worker role, profile, Task scope, and ownership changes. Other skills—including `bn`, TDD, decompilers, profilers, and domain specialists—may constrain how the assigned owner works but cannot assign, retain, or change execution ownership.

## Route in three stages

### 1. Classify the deliverable

- `software` — source, tests, builds, packaging, migration, implementation, or behavior-changing repair.
- `reverse` — evidence extraction, bounded semantic recovery, algorithm/behavior reconstruction, or analysis-database annotation.
- `mixed` — a Run containing both; split it into single-domain worker Tasks. `mixed` is never a worker Task domain.

Classify by requested output, not by the tool being used. Binary Ninja plugin code is software; Binary Ninja evidence recovery is reverse engineering.

### 2. Choose the execution shape

Use `direct`, one cohesive worker, or a multi-Task Run. Direct execution is an exception for a bounded task with a clear target, decision, scope, and focused validation. It is not sticky: scope expansion, unresolved root cause, a second independent failure/target, bulk input, repeated cases, cross-module work, or loss of the recorded basis after compaction requires re-routing before further inspection or mutation.

Read [references/task-routing.md](references/task-routing.md) when classification, direct eligibility, decomposition, batching, or parallel safety is not obvious or has changed.

### 3. Select one worker contract

For delegated work, read the selected domain reference, then the common Task envelope, then exactly one role contract:

| Task domain | Domain reference | Terra contract | Luna contract |
|---|---|---|---|
| `software` | [software.md](references/domains/software.md) | [software-terra.md](references/contracts/software-terra.md) | [software-luna.md](references/contracts/software-luna.md) |
| `reverse` | [reverse-engineering.md](references/domains/reverse-engineering.md) | [reverse-terra.md](references/contracts/reverse-terra.md) | [reverse-luna.md](references/contracts/reverse-luna.md) |

Read [references/contracts/task-envelope.md](references/contracts/task-envelope.md) once before creating Tasks. Do not read unused domain or role contracts. Keep one meaningful local loop together; do not split by file, test, function, address, or log line when the same mental model is required.

## Persist the route

Every delegated Task starts with exactly:

```text
[execution-owner: skill=orca-task-execution]
[task-domain: software|reverse]
[worker-role: terra|luna]
```

The coordinator chooses domain and role under this skill; it does not choose model or effort. [scripts/dispatch_worker.sh](scripts/dispatch_worker.sh) derives the only permitted profile and verifies the launch receipt:

| Domain / role | Derived profile |
|---|---|
| `software / terra` | `codex / gpt-5.6-terra / medium` |
| `software / luna` | `codex / gpt-5.6-luna / max` |
| `reverse / terra` | `codex / gpt-5.6-terra / high` |
| `reverse / luna` | `codex / gpt-5.6-luna / max` |

Record `execution_owner_skill`, Run domain, Task domain/role, execution shape, direct basis/revocation, context version, and outstanding Dispatches in compact Run Context. After compaction, recover these fields from durable Run/Task state; absence of a Run does not prove direct execution remains valid.

## Run and finish

Before Orca operations, activate the installed `orca-cli` and `orchestration` skills. For every fresh worker launch use `scripts/dispatch_worker.sh`; direct `worker-start` and caller-supplied profile overrides are forbidden. Read [references/runtime.md](references/runtime.md) only for delegated execution, placement, waiting, recovery, checkpointing, or review.

Finish when the requested behavior or reconstruction is accepted, required validation passes, every Dispatch is accounted for, persistent mutations are verified, and material risk or uncertainty is explicit.

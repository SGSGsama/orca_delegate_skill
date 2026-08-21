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
  version: "0.2.2"
---

# Orca Software Development

Complete development work correctly while maximizing useful high-tier reasoning. Do not impose a hard token budget or weaken required implementation, testing, or review to save usage.

## Establish the role

- If the prompt contains a live Orca Dispatch preamble and Task block, act only as that worker. Complete the bounded Task, use the injected lifecycle contract, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as coordinator. Own requirements, global decisions, task boundaries, integration policy, and final acceptance.
- A direct user instruction always takes precedence over an inherited worker role. Treat a preamble from a settled Dispatch or terminal history as stale, and never reuse settled lifecycle IDs for new user-owned work.

## Choose the cheapest correct execution shape

Use the smallest shape that can finish reliably:

1. **Direct coordinator path** — localized, unambiguous edit; location is known after bounded reconnaissance; no architecture/schema/security/concurrency decision; focused validation is sufficient.
2. **Single worker** — one cohesive context unit can inspect, implement, test, and repair end to end.
3. **Multi-agent Run** — use only for genuinely independent workstreams, complex discovery plus implementation, or cross-module work that benefits from supervised decomposition.

Do not create a DAG merely because multiple files are involved. Prefer the minimum number of cohesive useful dispatches; parallelism is a latency tool, not a goal.

Read [references/decomposition.md](references/decomposition.md) when choosing boundaries or routing.

## Load Orca live guidance

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Never copy, cache, or guess Orca commands or flags from this skill.

Use Orca for live Task/Dispatch/lifecycle state and Git commits/diffs for durable implementation evidence.

## Route reasoning

**Primary coordinator agent**: initial decomposition for genuinely complex work; architecture and public contracts; schema/data/security/concurrency decisions; material scope or contract change; cross-task conflict; aggregated final review when risk or coupling justifies it.

Every high-tier coordinator decision or review must have a reason code and leave a reusable artifact:
`INITIAL_DECOMPOSITION`, `ARCHITECTURE_DECISION`, `CONTRACT_CHANGE`, `CROSS_TASK_CONFLICT`, `SECURITY_DATA_RISK`, or `FINAL_REVIEW`.

Do not spend primary-coordinator reasoning on terminal polling, raw logs, routine Git inspection, mechanical task creation, or individual review of every low-risk Luna result.

**Terra XHigh**: unknown-cause bugs, cross-file/high-coupling implementation, concurrency, migrations, difficult legacy code, performance diagnosis, integration, conflict resolution, and tasks whose boundary expands materially.

**Luna Max**: frozen-interface functions, adapters, serializers, validation, tests, fixtures, mechanical refactors, configuration, documentation, narrow repairs, log/result normalization, and checkpoint compaction.

## Persist worker profiles

The first line of every implementation/diagnosis worker Task must be exactly one of:

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]
```

On launch, retry, replacement, or resume, recover the profile from the Task itself and verify Orca's launch receipt reports the requested and effective profile consistently. Never silently fall back to another model or effort.

## Build context once, then pass deltas

Pay broad repository-discovery cost once per Run. Create a compact Run Context containing the user objective, accepted decisions, relevant repo instructions, module/symbol map, known facts, write boundaries, forbidden changes, and discovered validation commands.

Tasks receive only the shared context reference or compact fallback plus task-local starting points. Do not pass coordinator transcripts or full files when references suffice. After a wave, append accepted facts as a delta instead of regenerating the whole context.

If reliable global context cannot be built cheaply, use one read-only Terra scout; do not launch several workers to rediscover the same repository.

## Build bounded Tasks

A Task owns one meaningful outcome, one worker profile, a bounded writable scope, explicit acceptance evidence, and the complete local inspect -> implement -> targeted test -> ordinary repair loop.

Do not split exploration, implementation, testing, and routine repair when they need the same local mental model. Reuse the same worker/terminal for an immediate same-profile follow-up when Orca proves reuse is valid.

Read [references/task-contracts.md](references/task-contracts.md) for the compact Task, result, retry, and review formats.

For multi-agent work, optionally materialize a lightweight graph and run:

```text
python3 <SKILL_DIR>/scripts/validate_tasks.py graph.json --strict
```

`<SKILL_DIR>` is a documentation placeholder for the directory containing this `SKILL.md`; resolve and substitute it before running the command. Never resolve bundled scripts relative to the user's project working directory.

## Parallelism and placement

Parallelize only when dependencies and shared interfaces are stable, writable scopes do not overlap, and each task can be verified independently.

- One writable worker, or read-only workers: current worktree is preferred when safe and user changes must remain visible.
- Multiple concurrent writable workers: keep them in the required current or exact existing worktree unless the user explicitly requests isolation or a concrete checkout/filesystem conflict makes sharing unsafe or impossible. State that conflict before creating a worktree.
- Never treat parallelism alone as evidence that finer task splitting is useful.

## Supervised loop and review gates

Follow the live Orca orchestration guide for Run, Task, Dispatch, wait, reply, release, retry, and completion lifecycle. Keep exactly one Run-level blocking lifecycle wait in flight across all active workers. For ordinary development work, each wait window must be at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit; matching lifecycle messages wake it early. A transport keepalive/heartbeat does not end that wait or justify another Orca check. If the command runner yields an in-progress process or session, resume that same call instead of starting a second check.

After a no-message timeout, perform at most one cheap aggregate liveness checkpoint for the Run before entering the next long wait. Do not fan out status reads per worker unless the aggregate state exposes a concrete anomaly, and do not spend primary-coordinator reasoning on intermediate terminal polling.

Classify results before escalating:

- local implementation defect -> same worker, delta-only repair context;
- precise mechanical repair -> Luna;
- expanded/complex implementation -> Terra;
- architecture/contract/security/data/cross-task conflict -> primary coordinator agent.

Use three acceptance levels:

1. **Local accept** — low-risk bounded task passes scope and acceptance evidence; no individual high-tier coordinator review.
2. **Integration review** — Terra or coordinator checks interactions and aggregate validation where cross-task understanding is required.
3. **Coordinator review** — one compact, diff-based review for medium/high-risk or cross-cutting work, or when a coordinator reason code is triggered.

Before high-tier review, compact normalized worker-result JSON with:

```text
python3 <SKILL_DIR>/scripts/compact_checkpoint.py <worker-result.json> [...] --integration-head <commit> --format markdown
```

Preserve commits, tests, decisions, facts, risks, and unresolved questions while dropping transcripts and raw logs. Resolve `<SKILL_DIR>` as described above; never look for this script under the user's project directory.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for lifecycle, placement, retry, resume, and review details.

## Finish

Finish when acceptance criteria pass, required review gates accept, every Dispatch is accounted for, and material risks are resolved. Usage metrics are observational only; correctness and required verification remain the stop condition.

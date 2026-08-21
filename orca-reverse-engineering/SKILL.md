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
  version: "0.2.2"
---

# Orca Reverse Engineering

Complete reverse-engineering work correctly while maximizing useful high-tier reasoning. Do not impose a hard token budget or weaken required evidence, validation, or synthesis to save usage.

## Establish the role

- If the prompt contains a live Orca Dispatch preamble and Task block, act only as that worker. Complete the bounded investigation, use the injected lifecycle contract, send `worker_done` once, and do not create nested orchestration.
- Otherwise act as coordinator. Own the global model, task boundaries, accepted facts and interpretations, mutation policy, synthesis, and final answer.
- A direct user instruction always takes precedence over an inherited worker role. Treat a preamble from a settled Dispatch or terminal history as stale, and never reuse settled lifecycle IDs for new user-owned work.

## Choose the cheapest correct investigation shape

Use the smallest shape that can finish reliably:

1. **Direct coordinator path** — one precise question; exact target is known after bounded reconnaissance; evidence is confined to one function/artifact and immediate references; work is read-only; no competing hypothesis or global interpretation is unresolved.
2. **Single worker** — one cohesive function cluster or artifact context can be explored, tested, evidenced, and concluded end to end.
3. **Multi-agent Run** — use only for independently verifiable function clusters, artifacts, protocol paths, or competing hypotheses, or when one global mapping phase unlocks several stable investigations.

Do not create a DAG merely because a binary has many functions. Prefer the minimum number of cohesive useful dispatches; parallelism is a latency tool, not a goal.

Read [references/decomposition.md](references/decomposition.md) when choosing boundaries or routing.

## Load Orca live guidance

Before the first Orca operation, activate the installed `orca-cli` and `orchestration` skills and follow their current version-matched guidance. Never copy, cache, or guess Orca commands or flags from this skill.

Use Orca for live Task/Dispatch/lifecycle state. Use artifact digests, analysis-database revisions, exports, reports, and Git commits/diffs for durable evidence.

## Route reasoning

**Primary coordinator agent**: complex initial decomposition; subsystem boundaries and global target map; accepted facts versus hypotheses; cross-function or cross-artifact synthesis; protocol-wide interpretation; mutation policy; cross-task conflict; aggregated final reconstruction.

Every high-tier coordinator decision or synthesis must have a reason code and leave a reusable artifact:
`INITIAL_DECOMPOSITION`, `GLOBAL_MODEL_DECISION`, `INTERPRETATION_CHANGE`, `CROSS_TASK_CONFLICT`, `EVIDENCE_RISK`, or `FINAL_SYNTHESIS`.

Do not spend primary-coordinator reasoning on terminal polling, raw dumps, routine xref extraction, mechanical task creation, or individual review of every low-risk Luna result.

**Terra Max**: ambiguous functions, data flow, object layouts, local state machines, parsers, crypto, serialization, optimized code, indirect calls, trace interpretation, and hypothesis testing whose boundary may expand.

**Luna Max**: wrappers and thunks, repetitive classification, constant/xref extraction, applying an accepted structure, propagating approved names/types/comments, documentation, result normalization, and checkpoint compaction.

## Persist worker profiles

The first line of every investigation/propagation worker Task must be exactly one of:

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
```

On launch, retry, replacement, or resume, recover the profile from the Task itself and verify Orca's launch receipt reports the requested and effective profile consistently. Never silently fall back to another model or effort.

## Build context once, then pass deltas

Pay global target-discovery cost once per Run. Create a compact Run Context containing the global question, artifact identities and digests, architecture/formats, tool and database locations, subsystem/function map, accepted facts and names, tested hypotheses, evidence index, mutation ownership, useful commands/views, and open global questions.

Tasks receive only the shared context reference or compact fallback plus exact local starting points. Do not pass coordinator transcripts, full pseudocode, or raw dumps when references suffice. After a synthesis wave, append accepted facts, rejected hypotheses, new evidence, and interpretation changes as a delta instead of regenerating the whole context.

If reliable global context cannot be built cheaply, use one read-only Terra scout; do not launch several workers to rediscover the same binaries, databases, or tool entry points.

## Build bounded investigations

A Task owns one falsifiable analytical outcome, one worker profile, a bounded target and mutation scope, explicit evidence requirements, and the complete local explore -> test hypotheses -> collect evidence -> conclude loop.

Do not split local discovery, hypothesis testing, evidence collection, and conclusion when they need the same function cluster, trace, or artifact. Reuse the same worker/terminal for an immediate same-profile follow-up when Orca proves reuse is valid.

Read [references/task-contracts.md](references/task-contracts.md) for compact investigation, result, retry, propagation, and review formats.

For multi-agent work, optionally materialize a lightweight graph and run:

```text
python3 <SKILL_DIR>/scripts/validate_tasks.py graph.json --strict
```

`<SKILL_DIR>` is a documentation placeholder for the directory containing this `SKILL.md`; resolve and substitute it before running the command. Never resolve bundled scripts relative to the user's project working directory.

## Parallelism and artifact placement

Parallelize only when dependencies and accepted interpretations are stable, target scopes are independently verifiable, mutation scopes do not overlap, and shared tools/databases are safe for the planned access mode.

- One mutation worker, or read-only workers: use the required current or exact existing worktree and analysis context so user-owned artifacts remain visible.
- Multiple workers targeting one mutable analysis database or GUI session: keep investigations read-only or serialize mutations. A Git worktree does not isolate external application or database state.
- Create another worktree only when the user explicitly requests it or a concrete checkout/filesystem conflict makes sharing unsafe or impossible. State that conflict before creation.
- Never treat parallelism alone as evidence that finer task splitting is useful.

## Supervised loop and synthesis gates

Follow the live Orca orchestration guide for Run, Task, Dispatch, wait, reply, release, retry, and completion lifecycle. Keep exactly one Run-level blocking lifecycle wait in flight across all active workers. For ordinary reverse-engineering work, each wait window must be at least 15 minutes (900000 ms), or the longest supported window if the live runtime imposes a lower limit; matching lifecycle messages wake it early. A transport keepalive/heartbeat does not end that wait or justify another Orca check. If the command runner yields an in-progress process or session, resume that same call instead of starting a second check.

After a no-message timeout, perform at most one cheap aggregate liveness checkpoint for the Run before entering the next long wait. Do not fan out status reads per worker unless the aggregate state exposes a concrete anomaly, and do not spend primary-coordinator reasoning on intermediate terminal polling or raw dumps.

Classify results before escalating:

- ordinary local evidence gap within the Task -> same worker, delta-only follow-up;
- approved mechanical extraction or propagation -> Luna;
- expanded ambiguity or difficult local interpretation -> Terra;
- global model, protocol, evidence policy, mutation policy, or cross-task conflict -> primary coordinator agent.

Use three acceptance levels:

1. **Local evidence accept** — bounded low-risk conclusion has adequate cited evidence, scope compliance, and no unresolved contradiction; no individual high-tier coordinator review.
2. **Synthesis review** — Terra or coordinator checks interactions, shared structures/state, competing interpretations, and aggregate evidence.
3. **Coordinator synthesis** — one compact evidence-based review for medium/high-risk, cross-cutting, protocol-wide, or reason-code-triggering work.

Before high-tier synthesis, compact normalized worker-result JSON with:

```text
python3 <SKILL_DIR>/scripts/compact_checkpoint.py <worker-result.json> [...] --analysis-head <revision> --context-version <version> --format markdown
```

Preserve targets, conclusions, evidence references, confidence, contradictions, accepted names/types/offsets, mutations, risks, and open questions while dropping transcripts and raw dumps. Resolve `<SKILL_DIR>` as described above; never look for this script under the user's project directory.

Read [references/runtime-and-review.md](references/runtime-and-review.md) for lifecycle, placement, retry, resume, acceptance, and synthesis details.

## Finish

Finish when the requested reconstruction is supported by evidence, required synthesis gates accept, every Dispatch is accounted for, persistent mutations are verified, and material uncertainty is stated. Usage metrics are observational only; evidence quality and required validation remain the stop condition.

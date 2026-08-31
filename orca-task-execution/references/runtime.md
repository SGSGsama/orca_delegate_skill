# Delegated Runtime

Load only for Orca dispatch, placement, waiting, recovery, checkpointing, or review.

## Launch contract

Before Orca operations, read the installed `orca-cli` and `orchestration` skills and follow their current command/lifecycle guidance. Orca owns live Run/Task/Dispatch/message state; Git, reports, artifact digests, and analysis revisions are durable evidence.

Start every fresh supervised worker through the absolute path to `scripts/dispatch_worker.sh`. It reloads the Task header from Orca state, derives the fixed domain/role profile, rejects foreign ownership, invalid/mixed domains, invalid roles, and caller overrides, then verifies requested and effective launch profiles. Never reconstruct profile from coordinator memory or call fresh `worker-start` directly, including after compaction.

Terminal reuse is allowed only when the next Task has the same domain/role, a coordinator-issued scope delta, and `worker-show` proves the retained terminal's effective profile equals the script-derived profile. Context reuse never widens authority.

## Delivery and placement

Complete one delivery gate before waiting: prove the intended Dispatch exists, the full Task was submitted, and the worker began processing. Staged text is not delivery; input and submit/Enter are one uninterrupted action. If delivery cannot be proven, report failure rather than duplicating the Task or worker.

- Prefer one writable worker in the required current/existing worktree when safe, especially with user-owned changes.
- Read-only workers may share state only when their tools are truly non-mutating.
- Concurrent writers require non-overlapping scopes and isolated mutable state. A Git worktree does not isolate GUI sessions, databases, trace stores, generated outputs, or other external state.

## Event-driven waiting

After an initial Dispatch wave, actionable Delivery, or true timeout, perform at most one bounded think-before-wait pass using accepted Run Context. It may refine the plan, perform one coordinator-owned global decision, dispatch stable independent work, or conclude that waiting is correct.

Choose one Run-level liveness interval, normally at least 15 minutes, and keep exactly one blocking lifecycle wait for all workers. Resume the same live wait handle through host yields and transport keepalives. While it is alive, do not poll workers, inspect partial output, infer health or elapsed progress, issue another Orca command, or narrate no-event status.

Only an actionable Delivery, a true completed timeout, or an explicit wait failure changes state. Process and acknowledge all Delivery messages and account for completed Dispatches. After a true timeout, perform at most one aggregate Run/task check before one new wait. A wait failure does not prove worker failure; follow version-matched recovery and establish at most one replacement waiter.

## Resume capsule

Preserve this compact control state across long waits and compaction:

```text
role=primary_coordinator execution_owner_skill=orca-task-execution
run_id=<id> run_domain=<software|reverse|mixed> context_version=<ref>
execution_shape=<direct|single-worker|multi-task>
direct_basis=<ref-or-na> direct_revoked=<true|false>
outstanding=<Task/Dispatch/domain/role/derived-profile/warm-terminal tuples>
dispatch_script=<absolute path> fresh_launch=script_only
delivery_gate=<state> wait_epoch=<id> think_before_wait=<state>
wait_state=<active|none> wait_handle=<exact handle>
event_filter=<version-matched filter> timeout_ms=<interval>
wake_on=delivery|true_timeout|wait_failure|user
next_action=<resume_same_wait-or-explicit lifecycle action>
```

Do not reinterpret these fields after compaction. If no active Run exists, re-evaluate and record direct eligibility before further inspection or mutation. If a wait is active, resume only that wait until a wake event occurs.

## Results and review

Require durable normalized reports for non-trivial Tasks. Compact each completed wave with `scripts/compact_checkpoint.py`; admit lifecycle decisions and compact evidence into coordinator context, not raw logs, dumps, terminal output, or full worker transcripts.

Locally accept bounded low-risk results whose scope and acceptance match. Reuse a warm Terra for ordinary same-lane/target repair. Escalate shared contracts, global models, cross-task contradictions, scope/domain changes, and final medium/high-risk behavior or reconstruction to the primary coordinator.

Finish only after every Dispatch is accounted for and persistent mutations and requested acceptance are verified.

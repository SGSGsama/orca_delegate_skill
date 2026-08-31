# Software Domain

Load for a delegated `software` Task. It defines domain decisions and acceptance; load only the selected Terra or Luna contract for worker behavior.

## Coordinator ownership

The primary coordinator owns user-visible behavior, architecture and input/output contracts, public API/schema/data/security/concurrency decisions, Task boundaries, material scope changes, and final behavioral/project acceptance.

Build Run Context once:

```text
Objective and behavior oracle
Accepted architecture/contracts
Relevant repository instructions and base state
Files, symbols, interfaces, and established facts
Write boundaries and forbidden changes
Known reproduction/build/test/lint commands
Open global decisions and context version
```

Keep one Terra composer for a cohesive semantic lane. Attach accepted Luna artifacts by reference and send only context deltas on continuation.

## Domain routing

- Terra: unknown-cause failures, coupled or cross-module semantics, migrations, concurrency/state machines, difficult integration, or repair needing a rich local model.
- Luna: frozen-contract implementation, bounded repetitive changes, tests/fixtures, validation, documentation/configuration, counterexample batches, or report normalization.
- Primary coordinator: shared contract/architecture changes, security/data/concurrency decisions, cross-task conflicts, and aggregate medium/high-risk review.

Terra may inspect Task-named logs and bounded adjacent context for one causal chain. Broad logs, repeated runs, platform matrices, or schema-bound bulk extraction belong to Luna.

## Acceptance

Require observable behavior and exact validation, not merely changed files. Preserve compatibility, error semantics, user-owned changes, and repository instructions. Locally accept a bounded result only when actual reads/writes stayed within contract, focused checks pass, no shared interface changed unexpectedly, and no material risk remains.

Use one aggregate coordinator review for cross-cutting or medium/high-risk work. A passing test does not excuse undeclared scope expansion or a worker-made shared-contract decision.

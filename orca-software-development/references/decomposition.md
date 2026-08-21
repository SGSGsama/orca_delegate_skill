# Development Decomposition

Load this file only when triage, task boundaries, routing, or safe parallelism are not already obvious.

## 1. Triage

Choose the smallest reliable execution shape.

### Direct coordinator

Use when all are true:

- behavior and acceptance are unambiguous;
- bounded reconnaissance locates the change;
- patch is localized and semantically small, typically one or two tightly coupled files;
- no unresolved public API, schema, migration, concurrency, security, data-integrity, or root-cause decision exists;
- one focused validation path can establish completion;
- delegation would cost at least as much context preparation as execution.

Stop the direct path once broad discovery or cross-module reasoning becomes necessary.

### Single worker

Prefer one worker when the same mental model is needed for local discovery, implementation, tests, and ordinary repair. Do not manufacture separate scout/coder/tester Tasks for one cohesive module.

### Multi-agent

Use when there are multiple independently verifiable outcomes, or when one global discovery/decision phase can unlock several stable implementation boundaries.

## 2. Build Run Context once

Keep a compact shared packet or reference with:

```text
Objective
Accepted architecture/contracts
Relevant repository instructions
Base revision and user-owned local changes
Relevant modules, files, symbols, interfaces
Established facts and rejected assumptions
Writable boundaries and forbidden changes
Known build/test/lint/reproduction commands
Open global questions
Context version/digest
```

Workers receive task-local starting points plus this reference. Update later waves with deltas: new accepted facts, contract changes, new commands, or invalidated assumptions.

If this packet cannot be built without broad exploration, dispatch exactly one read-only Terra scout first.

## 3. Decompose by outcome, not file count

A good Task owns:

- one meaningful result;
- one worker profile;
- one cohesive local context;
- one bounded write surface or read-only scope;
- explicit invariants and forbidden changes;
- exact acceptance evidence;
- a clear escalation boundary.

Bad split:

```text
T1 edit service.ts
T2 edit repository.ts
T3 add tests
```

Better split:

```text
T0 freeze transaction/compatibility contract
T1 implement the cross-module transaction flow + local tests
T2 implement the independent serializer under the frozen contract
T3 integrate and run aggregate validation
```

## 4. Routing

### Primary coordinator agent

Use only when a global decision is actually needed:

- complex initial decomposition;
- architecture or public contract;
- schema/data/security/concurrency decision;
- material contract change;
- conflict between worker findings;
- aggregate medium/high-risk review.

A high-tier coordinator decision or review must produce a TaskGraphLite, Decision Record, revised contract, conflict resolution, or review verdict.

### Terra XHigh

Use for unknown-cause failures, broad local reasoning, high coupling, migrations, hard concurrency/state-machine work, performance diagnosis, difficult test failures, integration, or expanded scope.

### Luna Max

Use for precise implementation under frozen interfaces, tests, adapters, repetitive changes, narrow repairs, documentation/configuration, and result/checkpoint compaction.

## 5. Safe parallelism

Run Tasks concurrently only when all are true:

1. dependency prerequisites are complete;
2. shared interfaces are frozen;
3. writable scopes do not overlap;
4. one task does not require another task's unaccepted output;
5. tests/build steps will not corrupt shared mutable state, or workers are isolated;
6. each task has independent acceptance evidence.

Prefer **minimum cohesive useful dispatches**. More agents often increase repeated code reading, duplicated reasoning, merge conflict, and review cost.

## 6. Replan threshold

Do not repeatedly replan at the primary-coordinator level. Replan only for material new facts, invalidated assumptions, contract changes, dependency changes, or scope expansion that invalidates current Tasks.

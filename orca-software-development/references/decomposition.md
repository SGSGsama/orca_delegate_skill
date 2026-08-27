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

Prefer one Terra composer/context owner when the same mental model is needed for local discovery, implementation, integration, tests, and ordinary repair. Do not manufacture separate scout/coder/tester Tasks for one cohesive module. A single Luna worker is preferable only when the contract is frozen and the work is a self-contained mechanical batch that needs no broad rediscovery.

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

For each coupled semantic area, add a compact lane manifest:

```text
Lane ID and current Terra composer/terminal
Relevant context version, accepted design, and Task/product input-output contract
Files, symbols, interfaces, invariants, and commands already inspected
Accepted Luna leaf artifacts
Local decisions and rejected alternatives
Completed and pending acceptance checks
Unresolved local questions and next starting point
```

Keep the same Terra composer while work remains inside that lane. A later Dispatch to that terminal carries only the Task delta and newly accepted leaf artifacts. Replace the composer only for failure, unavailable capability, explicit independent review, or a boundary change large enough to justify rebuilding context.

## 3. Decompose by outcome, not file count

A good Task owns:

- one meaningful result;
- one worker profile;
- one cohesive local context;
- one bounded write surface or read-only scope;
- explicit invariants and forbidden changes;
- exact acceptance evidence;
- a clear escalation boundary.

Before splitting, apply the context-affinity test. If two proposed Tasks require substantially the same files, local decisions, execution state, or failure interpretation, keep them in one Terra composer lane or consecutive Dispatches to the same Terra. A split is justified when it creates an independently acceptable outcome, a genuinely parallel boundary, a different required capability, or useful failure isolation.

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

Prefer primary-coordinator attention for:

- complex initial decomposition;
- architecture, Task/product input-output contract, or public contract;
- user-visible behavior and acceptance oracle;
- schema/data/security/concurrency decision;
- material contract change;
- conflict between worker findings;
- aggregate medium/high-risk review.

A high-tier coordinator decision or review must produce a TaskGraphLite, Decision Record, revised contract, conflict resolution, or review verdict.

### Terra XHigh composer

Use as the semantic lane composer for unknown-cause failures, broad local reasoning, high coupling, migrations, hard concurrency/state-machine work, performance diagnosis, difficult test failures, integration of accepted Luna leaf artifacts, or coordinator-approved expanded scope. Terra produces the cohesive review-ready result but does not dispatch nested workers.

Terra may inspect Task-named logs and bounded adjacent context when causal interpretation requires raw evidence. It must not independently broaden that inspection into corpus-wide enumeration, repeated-run/platform comparison, or schema-driven bulk extraction; return `NEED_BULK_EVIDENCE` for a Luna pass. Neither a warm lane nor a transitive code/log discovery expands the current Task authority without a coordinator-issued delta.

### Luna Max

Use for precise implementation under frozen interfaces, tests, adapters, repetitive changes, narrow independent repairs, documentation/configuration, and result/checkpoint compaction. Luna capacity is abundant, but context preparation, task lifecycle, and result integration still matter.

Prefer batch-shaped Luna outcomes such as "apply this accepted transformation to this bounded set and validate all items." Do not create one Task per file, test, endpoint, or generated item. If a batch encounters a contradictory item, record and skip that item where safe, continue independent items, and return one grouped report.

Because Luna is cheap, use bounded redundant Luna work when it improves evidence: regression search, generated counterexamples, compatibility matrices, or an independent check against a frozen contract. Feed those results into the same wave checkpoint; normally request primary-coordinator attention when a discrepancy changes a global decision, while preserving the coordinator's ability to inspect any result.

### Cost-aware placement test

Use the primary coordinator for design, input/output and behavior contracts, a global decision, the direct-path exception, and final behavioral/project review. Use Terra as composer when the work creates or depends on a rich local mental model or must integrate leaf outputs. Use Luna when all required semantics can fit in a frozen contract plus compact context/inputs. Keep work with a warm composer whenever reassignment would require the receiver to reread or rederive most of the lane context.

## 5. Safe parallelism

Run Tasks concurrently only when all are true:

1. dependency prerequisites are complete;
2. shared interfaces are frozen;
3. writable scopes do not overlap;
4. one task does not require another task's unaccepted output;
5. tests/build steps will not corrupt shared mutable state, or workers are isolated;
6. each task has independent acceptance evidence.

Prefer **minimum cohesive useful dispatches**. More agents often increase repeated code reading, duplicated reasoning, merge conflict, and review cost.

Measure fan-out by independent acceptance units, not source-file or input-item count. Cheap Luna capacity should increase the breadth of a batch or the number of truly independent batches, not the number of coordinator conversations. Aggregate each completed wave into one checkpoint before primary-coordinator review.

## 6. Replan threshold

Avoid routine primary-coordinator replanning. Replan there for material new facts, invalidated assumptions, contract changes, dependency changes, scope expansion that invalidates current Tasks, or whenever direct coordinator judgment would materially improve the result.

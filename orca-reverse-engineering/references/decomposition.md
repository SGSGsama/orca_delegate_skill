# Reverse-Engineering Decomposition

Load this file only when triage, investigation boundaries, routing, or safe parallelism are not already obvious.

## 1. Triage

Choose the smallest reliable investigation shape.

### Direct coordinator

Use when all are true:

- the request asks one precise semantic or factual question;
- bounded reconnaissance locates the exact binary, function, address, symbol, or artifact;
- the evidence path is limited to one function/artifact and immediate callers, callees, or xrefs;
- no competing hypothesis, protocol/state-machine recovery, object-layout inference, crypto/serialization reconstruction, or cross-artifact correlation is required;
- the work is read-only and requires no broad naming, typing, annotation, or documentation propagation;
- delegation would cost at least as much context preparation as direct evidence recovery.

Stop the direct path once broad discovery, competing explanations, or cross-subsystem synthesis becomes necessary.

### Single worker

Prefer one worker when the same local mental model is needed for function-cluster exploration, hypothesis testing, evidence collection, and conclusion. Do not manufacture separate xref-reader, decompiler, and evidence-writer Tasks for one cohesive cluster.

### Multi-agent

Use when there are multiple independently falsifiable outcomes, separate artifacts or function clusters, read-only competing hypotheses, or one global mapping/contract phase can unlock several stable investigations.

## 2. Build Run Context once

Keep a compact shared packet or reference with:

```text
Global objective and requested output
Artifact identities, hashes, architecture, formats, and base revisions
Tool, database, session, trace, capture, and project locations
Accepted subsystem/function map and important entry points
Accepted names, types, offsets, constants, state, and protocol facts
Evidence index with addresses/functions/artifact references
Tested and rejected hypotheses
Mutation ownership and forbidden changes
Known commands, scripts, tool views, and reproducible queries
Open global questions
Context version/digest
```

Workers receive task-local starting points plus this reference. Update later waves with deltas: accepted facts, rejected hypotheses, interpretation changes, new evidence, invalidated assumptions, and mutation results.

If this packet cannot be built without broad exploration, dispatch exactly one read-only Terra scout first.

## 3. Decompose by falsifiable outcome

A good Task owns:

- one meaningful analytical result;
- one worker profile;
- one cohesive local evidence context;
- one bounded target plus read/mutation scope;
- explicit known facts and competing hypotheses;
- exact evidence and acceptance requirements;
- a clear escalation boundary.

Bad split:

```text
T1 decompile handler_A
T2 list xrefs for handler_A
T3 write the conclusion
```

Better split:

```text
T0 freeze accepted message IDs, entry points, and evidence vocabulary
T1 reconstruct receive/decode path with local hypothesis tests and evidence
T2 independently reconstruct send/encode path under the accepted vocabulary
T3 synthesize message layout and resolve asymmetric observations
```

## 4. Routing

### Primary coordinator agent

Use when a global decision is actually needed:

- complex initial decomposition;
- subsystem boundaries or global target map;
- protocol-wide interpretation or shared structure contract;
- material interpretation or mutation-policy change;
- conflict between worker findings;
- aggregate medium/high-risk synthesis.

A high-tier coordinator decision or synthesis must produce a TaskGraphLite, Decision Record, revised interpretation contract, conflict resolution, or synthesis verdict.

### Terra Max

Use for ambiguous functions, nontrivial data flow, object layouts, local state machines, parsers, crypto, serialization, optimized code, indirect calls, trace interpretation, difficult tool output, or hypothesis testing whose boundary may expand.

### Luna Max

Use for constrained wrappers/thunks, repetitive classification, constant/xref extraction, applying an accepted structure, approved name/type/comment propagation, documentation, and result/checkpoint compaction.

## 5. Safe parallelism

Run Tasks concurrently only when all are true:

1. dependency prerequisites are complete;
2. shared names, types, protocol vocabulary, and interpretation contracts are stable;
3. target and mutation scopes do not overlap;
4. one task does not require another task's unaccepted conclusion;
5. shared analysis databases, GUI sessions, trace sources, and output files are read-only or proven safe for concurrent access;
6. each task has independent acceptance evidence.

Do not use Git worktrees as a substitute for isolating an external GUI session or mutable analysis database. Serialize mutations when independent copies and a verified merge strategy do not exist.

Prefer **minimum cohesive useful dispatches**. More agents often increase repeated decompilation, duplicated xref traversal, incompatible naming, contradictory mutations, and synthesis cost.

## 6. Replan threshold

Do not repeatedly replan at the primary-coordinator level. Replan only for material new evidence, invalidated assumptions, interpretation changes, dependency changes, artifact mismatch, or scope expansion that invalidates current Tasks.

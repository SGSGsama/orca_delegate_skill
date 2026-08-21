# Reverse-Engineering Decomposition

Load this file when routing, investigation boundaries, evidence flow, or safe parallelism is not already obvious.

## 1. Route by reverse-engineering work shape

Choose roles from semantic coupling, target locality, input volume, mutability, and falsifiability. The examples below illustrate the dimensions; they are not a closed task catalog.

### Primary coordinator: global semantic and adversarial work

Prefer direct primary-coordinator ownership when the hard part is the global interpretation itself:

- reconstructing an algorithm, end-to-end control/data flow, protocol behavior, or system-wide state model;
- reasoning about complex obfuscation, virtualization, anti-analysis, integrity checks, opaque dispatch, or other protection/countermeasure interactions;
- correlating many functions, subsystems, binaries, captures, or competing global hypotheses;
- defining the evidence standard, accepted vocabulary, mutation policy, or behavioral validation oracle;
- resolving contradictions that would change the global model;
- synthesizing local results into the requested reconstruction and validating it against observable behavior.

The coordinator may inspect code, IL, traces, or artifacts directly whenever that is the clearest way to solve the semantic core. Delegate supporting evidence work without delegating away the global reasoning that makes the result coherent.

### Terra: bounded local semantics

Use Terra for a precise function or tightly coupled local cluster whose meaning can be concluded with bounded context:

- function purpose, inputs/outputs, side effects, error paths, callers/callees, and local data/control flow;
- a localized structure layout, field use, state transition, parser stage, serializer stage, indirect call, or optimized routine;
- a precise local hypothesis test, contradiction check, type/name proposal, or difficult decompiler/IL interpretation;
- local validation needed by a coordinator-owned global algorithm or protection analysis.

Keep exploration, hypothesis testing, evidence collection, and conclusion together. Reuse the same Terra terminal for adjacent questions sharing the same target context. If the conclusion expands into system-wide algorithm or adversarial reasoning, return the local evidence and escalate the global interpretation instead of independently rediscovering the whole target.

### Luna: high-volume evidence processing

Use Luna when input volume and repetitive evidence handling dominate:

- logs, runtime traces, packet captures, crash/event streams, memory or register dumps, and large tool exports;
- large string, xref, constant, import/export, call-edge, candidate-function, or sample sets;
- corpus or version comparison, coverage accounting, repetitive classification, search, filtering, normalization, and report compaction;
- applying an accepted mapping across names, types, comments, annotations, or other bounded mutations;
- broad counterexample or anomaly search under an already stated hypothesis and evidence schema.

A Luna Task must identify the input manifest, extraction/classification schema, coverage requirement, exception policy, and output index. It returns references, counts, clusters, and anomalies rather than copying raw input. If an item requires non-local semantic judgment, preserve the evidence and flag it for Terra or the primary coordinator.

### Multi-agent Run

Use a mixed Run when these transforms are genuinely useful together: Luna reduces large inputs into indexed evidence, Terra resolves bounded local meanings, and the primary coordinator reconstructs global algorithms, behavior, or protection logic. Skip any stage that would merely re-read another role's work without adding evidence.

## 2. Build context in three layers

### Global model

Owned by the primary coordinator:

```text
Objective and requested output
Artifact identities, hashes, architecture, formats, and revisions
Subsystem/function map and important entry points
Accepted global behavior, vocabulary, and evidence standard
Global hypotheses, contradictions, and protection assumptions
Mutation ownership and forbidden changes
Tool/database/session locations and reproducible commands
Context version/digest
```

### Evidence index

Usually produced or extended by Luna:

```text
Input manifest and processed coverage
Stable event/address/function/sample identifiers
Extracted facts, clusters, counts, and candidate anomalies
Raw-source references for drill-down
Skipped, malformed, or ambiguous items
Schema/version and reproducible extraction command
```

### Local target packet

Given to Terra:

```text
Exact functions/addresses/trace ranges/tool views
One local semantic question and competing hypotheses
Relevant global facts and vocabulary
Only the evidence-index slices needed for this target
Required local evidence and acceptance standard
Mutation scope, if any
Prior local conclusion and delta for terminal reuse
```

Do not make every Terra worker load the full binary history or entire logs. Do not ask Luna to rediscover global meaning while processing bulk input. Update global context with accepted deltas rather than coordinator transcripts.

## 3. Decompose by evidence transformation

A good delegated Task performs one independently checkable transformation:

```text
bulk raw inputs --Luna--> indexed evidence and coverage
bounded target + evidence slice --Terra--> local semantic conclusion
local conclusions + global evidence --primary coordinator--> algorithm/behavior/adversarial synthesis
```

This is a routing model, not a mandatory linear pipeline. The coordinator may directly solve global work, Luna and Terra Tasks may run independently, and a single worker may be enough. Avoid separate decompiler, xref-reader, and report-writer Tasks when they share one local question.

## 4. Routing corrections

| New condition | Route |
|---|---|
| Ordinary evidence gap inside one local target | Same Terra, delta-only follow-up |
| Local target expands to adjacent tightly coupled functions | Same Terra if context remains bounded |
| Local result changes the global algorithm or protection model | Primary coordinator |
| More logs/traces/dumps/candidates are needed | Luna bulk evidence pass |
| Bulk evidence exposes a precise semantic anomaly | Terra for local meaning; coordinator if globally coupled |
| Accepted mapping needs broad propagation | Luna batch |
| Cross-target contradiction or evidence-policy change | Primary coordinator |

Changing workers unnecessarily repays artifact loading, tool orientation, decompilation, and target-understanding cost.

## 5. Safe parallelism

Parallelize Luna batches when their input sources or output partitions are independent and share one frozen schema. Parallelize Terra analyses when local targets are independently falsifiable and do not depend on unaccepted interpretations. Do not parallelize mutations against the same analysis database, GUI session, trace store, or output file without proven isolation and merge semantics.

Measure fan-out by independent evidence products or semantic questions, not function, address, log-line, or sample count. Prefer broad Luna batches and cohesive Terra targets. A Git worktree does not isolate external mutable analysis state.

## 6. Replan threshold

Request primary-coordinator replanning when local scope becomes global, a protection assumption fails, evidence coverage is inadequate, an artifact identity changes, or accepted interpretations/dependencies become invalid. Ordinary local evidence gaps stay with the same Terra; ordinary bulk-input gaps extend the Luna manifest or batch.

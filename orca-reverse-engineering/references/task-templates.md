# Reverse-Engineering Task Templates

Read only the template matching the next bounded task. Replace every angle-bracket placeholder and remove irrelevant fields before dispatch.

`Shared context packet` must contain the accepted Run-level target map, tool/database locations, known call paths and structures, tested hypotheses, mutation ownership, and useful commands or views. Inline it unless every worker is proven to share the referenced path. `Local starting points` should name exact functions, addresses, xrefs, traces, or artifacts so the worker does not repeat global discovery.

## Unknown function or cluster

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Objective: Determine <specific semantic question>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact functions, addresses, xrefs, traces, and tool views>.
Scope: <binary/module/functions/addresses>. Read-only unless stated otherwise.
Available artifacts: <database, binary, pseudocode, traces, symbols>.
Known facts: <facts with evidence>.
Hypotheses to test: <competing explanations>.
Inspect: callers, callees, inputs, outputs, side effects, error paths, important offsets/constants, and algorithm stages.
Required evidence: cite addresses/functions/xrefs/traces that distinguish the hypotheses.
Do not: <excluded regions or mutations>.
Complete in this Task: local exploration, hypothesis testing, evidence collection, and conclusion.
Return: conclusion; evidence; confidence; alternatives/contradictions; useful names/types; next investigation.
```

## Structure or object layout

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Objective: Recover the meaning and type of fields in <object/context>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact functions, offsets, accesses, xrefs, and tool views>.
Scope: accesses from <functions/address range>.
Seed mapping: <accepted offsets and types>.
Questions: field widths, signedness, ownership/lifetime, aliasing, invariants, and state-dependent meanings.
Required evidence: representative reads/writes and conflicts for every proposed field.
Mutation policy: propose only | apply only the explicitly accepted mapping.
Return: offset table; confidence per field; incompatible observations; follow-up targets.
```

## Protocol or state machine

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Objective: Reconstruct <protocol/state transition subset>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact handlers, message IDs, traces, captures, and tool views>.
Scope: <entry points, handlers, message IDs, states>.
Known observations: <captures/traces/constants>.
Questions: message layout, transition guards, state updates, retries/errors, cryptographic or serialization stages.
Return: states/transitions or message schema; evidence for each edge/field; unresolved ambiguity; suggested discriminating test.
```

## Resolve a contradiction

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Disputed claim: <one exact claim>.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact conflicting functions, observations, and tool views>.
Hypothesis A and evidence: <summary>.
Hypothesis B and evidence: <summary>.
Scope: <smallest code/artifact region able to distinguish them>.
Required result: identify which hypothesis fits, whether neither fits, decisive evidence, and residual uncertainty.
Do not broaden into a full subsystem analysis.
```

## Propagate an accepted interpretation

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: Apply the approved mapping below without new semantic invention.
Shared context packet: <compact inline packet or proven shared path plus inline fallback>.
Local starting points: <exact database/files/functions and accepted mapping source>.
Writable scope: <database/files/functions>.
Approved mapping: <old -> new names, offsets -> fields/types, comments>.
Validation: <reload/query/export checks>.
Stop and escalate if any use contradicts the mapping; do not force the rename/type.
Return: applied items; skipped/conflicting items; modified artifacts; validation result.
```

# Reverse-Engineering Task Templates

Read only the template matching the next bounded task. Replace every angle-bracket placeholder and remove irrelevant fields before dispatch.

## Unknown function or cluster

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Objective: Determine <specific semantic question>.
Scope: <binary/module/functions/addresses>. Read-only unless stated otherwise.
Available artifacts: <database, binary, pseudocode, traces, symbols>.
Known facts: <facts with evidence>.
Hypotheses to test: <competing explanations>.
Inspect: callers, callees, inputs, outputs, side effects, error paths, important offsets/constants, and algorithm stages.
Required evidence: cite addresses/functions/xrefs/traces that distinguish the hypotheses.
Do not: <excluded regions or mutations>.
Return: conclusion; evidence; confidence; alternatives/contradictions; useful names/types; next investigation.
```

## Structure or object layout

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Objective: Recover the meaning and type of fields in <object/context>.
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
Scope: <entry points, handlers, message IDs, states>.
Known observations: <captures/traces/constants>.
Questions: message layout, transition guards, state updates, retries/errors, cryptographic or serialization stages.
Return: states/transitions or message schema; evidence for each edge/field; unresolved ambiguity; suggested discriminating test.
```

## Resolve a contradiction

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Disputed claim: <one exact claim>.
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
Writable scope: <database/files/functions>.
Approved mapping: <old -> new names, offsets -> fields/types, comments>.
Validation: <reload/query/export checks>.
Stop and escalate if any use contradicts the mapping; do not force the rename/type.
Return: applied items; skipped/conflicting items; modified artifacts; validation result.
```

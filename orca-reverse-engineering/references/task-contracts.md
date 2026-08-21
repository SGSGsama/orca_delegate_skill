# Compact Reverse-Engineering Task Contracts

Prefer short text Task specs. The primary coordinator agent should decide boundaries, accepted interpretations, and mutation policy; Luna or a deterministic helper can materialize boilerplate.

## Worker Task

The worker profile must be the first line.

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Task: T2
Type: investigation | structure | protocol | hypothesis-test | review | propagation
Objective: <one falsifiable analytical outcome>
Context: <Run Context ref/version + short fallback facts>
Starts: <exact artifacts/functions/addresses/xrefs/traces/tool views>
Depends: <task IDs or none>
Read: <bounded artifacts/functions/address ranges>
Mutate: <bounded databases/files/functions; none for read-only>
Forbidden: <regions/artifacts/names/types/interpretations that must not change>
Known facts: <accepted facts with evidence references>
Hypotheses: <competing explanations to test>
Evidence: <addresses/functions/xrefs/traces required to distinguish them>
Acceptance: <observable conclusion, confidence standard, and reproducible checks>
Escalate: <what invalidates the contract or needs a global interpretation decision>
Return: conclusion; evidence refs; confidence; alternatives/contradictions; mutations; next target.
```

Use the Luna profile instead only when the analytical pattern and approved mapping are already constrained.

## Function or cluster investigation

```text
Objective: determine <specific semantic question>
Inputs/outputs: <registers/arguments/returns/buffers/state>
Inspect: callers; callees; side effects; error paths; offsets/constants; algorithm stages
Hypotheses: <plausible meanings>
Required evidence: <observations able to falsify each hypothesis>
Return: conclusion; causal/data-flow explanation; cited evidence; confidence; unresolved ambiguity
```

## Structure or object layout

```text
Objective: recover <object/context> fields
Seed mapping: <accepted offsets/types>
Questions: widths; signedness; ownership/lifetime; aliasing; invariants; state-dependent meanings
Required evidence: representative reads/writes and conflicts for every proposed field
Mutation policy: propose only | apply only the explicitly accepted mapping
Return: offset table; confidence per field; incompatible observations; follow-up targets
```

## Protocol or state machine

```text
Objective: reconstruct <protocol/state subset>
Scope: <entry points/handlers/message IDs/states>
Known observations: <captures/traces/constants>
Questions: layout; transition guards; state updates; retries/errors; crypto/serialization stages
Return: schema or transition model; evidence per field/edge; unresolved ambiguity; discriminating test
```

## Contradiction-resolution Task

```text
Disputed claim: <one exact claim>
Hypothesis A / evidence: <compact references>
Hypothesis B / evidence: <compact references>
Scope: <smallest region or artifact able to distinguish them>
Required result: which hypothesis fits, whether neither fits, decisive evidence, residual uncertainty
Forbidden: broad subsystem analysis or mutation
```

## Propagation Task

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Objective: apply the approved mapping without new semantic invention
Approved mapping: <old -> new names; offsets -> fields/types; comments>
Mutate: <exact databases/files/functions>
Validation: <reload/query/export checks>
Stop: any contradictory use or evidence; do not force the mapping
Return: applied items; skipped/conflicting items; modified artifacts; validation result
```

## Same-worker follow-up delta

Do not resend the entire Task for an ordinary local evidence gap:

```text
Follow-up-of: <Task/Dispatch/result ref>
Reason: LOCAL_EVIDENCE_GAP
Unmet acceptance: <claim/evidence/check>
New evidence: <minimal observation/ref>
Scope delta: <usually none>
Required investigation: <specific distinguishing question>
Return: updated conclusion + evidence + confidence
```

Escalate instead if the result requires changing the global subsystem map, shared protocol/structure interpretation, evidence standard, mutation policy, or materially expanding scope.

## Worker result

Normalize results to this compact shape before synthesis:

```text
Task / status
Target and artifact identity
Base / analysis revision
Conclusion
Evidence references
Confidence
Alternatives / contradictions
Accepted or proposed names, types, offsets, states, or schemas
Mutations and validation
New facts
Risks / unresolved questions
Scope deviation
Recommended next action
One-paragraph summary
```

Do not attach full transcripts, raw disassembly, complete pseudocode, full traces, or copied binaries/databases.

## TaskGraphLite sidecar

When deterministic preflight is useful, materialize only orchestration facts. Use relative logical scope identifiers such as `binary/main/functions/receive/**` or `analysis/main.bndb/types/**`; keep absolute tool/database paths in the text Task, not this sidecar.

```json
{
  "tasks": [
    {
      "id": "T1",
      "role": "terra-max",
      "depends_on": [],
      "read": ["binary/main/functions/receive/**"],
      "mutate": [],
      "risk": "medium"
    },
    {
      "id": "T2",
      "role": "luna-max",
      "depends_on": ["T1"],
      "read": ["analysis/main.bndb/functions/receive/**"],
      "mutate": ["analysis/main.bndb/names/receive/**"],
      "risk": "low"
    }
  ]
}
```

This sidecar is for validation, not a requirement that the primary coordinator agent emit verbose JSON.

## Compact synthesis packet

High-tier synthesis receives only:

```text
User objective and requested reconstruction
Artifact identities/digests and accepted subsystem map
Accepted interpretation decisions
Evidence index and analysis revision references
Compact checkpoint
Material contradictions, risks, and unresolved questions
Requested synthesis reason code
```

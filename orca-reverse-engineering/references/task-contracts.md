# Compact Reverse-Engineering Task Contracts

The primary coordinator owns the global semantic problem, evidence standard, and final reconstruction. Delegated Tasks should transform bulk inputs into indexed evidence or answer one bounded local semantic question; they are not a substitute for coordinator-owned algorithm or protection reasoning.

## Common worker Task

The worker profile must be the first line.

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Task: T2
Type: bulk-evidence | function | cluster | local-dataflow | local-structure | hypothesis-test | propagation | validation
Objective: <one independently checkable evidence product or local conclusion>
Role intent: bulk-evidence | local-semantics
Context: <global Run Context ref/version + compact fallback facts>
Starts: <exact artifact/function/address/trace/tool/export references>
Depends: <task IDs or none>
Read: <bounded artifacts/functions/address ranges/input manifests>
Mutate: <bounded databases/files/functions; none for read-only>
Forbidden: <regions/artifacts/interpretations/mutations that must not change>
Accepted vocabulary: <names/types/states/evidence identifiers already fixed>
Acceptance: <coverage or cited-evidence requirements and reproducible checks>
Escalate: <what turns this into global semantic/adversarial reasoning or changes policy>
Return: <normalized report path, evidence refs, conclusion/coverage, anomalies, context delta>
```

Use the Terra profile for bounded local semantics. Use this Luna profile when bulk input handling, repetitive extraction/classification, coverage, or propagation dominates:

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
```

## Luna bulk-evidence Task

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Type: bulk-evidence
Objective: transform <large input set> into <indexed evidence product>
Input manifest: <logs/traces/dumps/exports/candidates/samples + identities>
Schema: <fields, event keys, address/function IDs, classifications, output format>
Queries: <facts, clusters, correlations, anomalies, or counterexamples to extract>
Coverage: <processed/skipped/error accounting required>
Raw-source refs: <how every output item links back to source>
Exception policy: record ambiguous/semantic items; continue independent safe items
Forbidden: infer global algorithm/protection meaning not stated by the schema
Return: evidence index; coverage counts; clusters; anomalies; malformed/skipped items; reproducible command; report path
```

Use one batch per coherent input source and evidence question, not one Task per line, event, address, function candidate, or sample.

## Terra function or local-cluster Task

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Type: function | cluster | local-dataflow | hypothesis-test
Objective: determine <one bounded semantic question>
Target: <exact function(s), addresses, IL/tool views, artifact revision>
Global facts: <only accepted vocabulary/model facts needed locally>
Evidence slice: <specific Luna index entries, traces, callers/callees, xrefs>
Inputs/outputs: <registers/arguments/returns/buffers/state>
Hypotheses: <plausible local meanings>
Inspect: <call/data/control flow, side effects, error paths, offsets/constants>
Acceptance: <evidence able to distinguish hypotheses and reproduce conclusion>
Escalate: target expands beyond a tight cluster; conclusion changes global algorithm/protection model; evidence policy is inadequate
Return: local conclusion; causal/data-flow explanation; cited evidence; confidence; rejected alternatives; residual ambiguity; report path
```

Keep the complete local explore -> test -> evidence -> conclude loop with the same Terra. For an adjacent target that uses substantially the same context, reuse the terminal and send only a delta.

## Terra local structure or state Task

```text
[worker-profile: agent=codex model=gpt-5.6-terra effort=max]
Type: local-structure
Objective: recover <bounded object/state/parser-stage subset>
Target: <exact functions, offsets, state values, or transition slice>
Seed mapping: <accepted offsets/types/names/states>
Questions: widths; signedness; ownership/lifetime; aliasing; local invariants; transition guards
Evidence slice: <representative reads/writes/traces for every proposed field or edge>
Mutation policy: propose only | apply only explicitly accepted mapping
Escalate: meaning depends on protocol-wide state, global algorithm, or protection mechanism
Return: local mapping/model; evidence per field/edge; confidence; conflicts; mutations; report path
```

## Luna propagation Task

```text
[worker-profile: agent=codex model=gpt-5.6-luna effort=max]
Type: propagation
Objective: apply the accepted mapping without new semantic invention
Approved mapping: <old -> new names; offsets -> fields/types; comments/annotations>
Input manifest: <exact databases/files/functions/items>
Mutate: <exact scopes>
Validation: <reload/query/export checks and processed/skipped counts>
Stop item: contradictory use or evidence; do not force the mapping
Return: applied items; skipped/conflicting items; modified artifacts; validation; report path
```

## Contradiction routing

For a contradiction confined to one bounded target, use Terra:

```text
Disputed local claim: <one exact claim>
Hypothesis A / evidence: <compact references>
Hypothesis B / evidence: <compact references>
Target: <smallest local region able to distinguish them>
Return: decisive evidence, local conclusion, residual ambiguity
```

If resolving it changes the global algorithm, system behavior, protection model, evidence standard, or mutation policy, send the evidence references to the primary coordinator instead of creating a broader Terra Task.

## Same-worker follow-up delta

Do not resend the entire Task for an ordinary local evidence gap:

```text
Follow-up-of: <Task/Dispatch/result ref>
Reason: LOCAL_EVIDENCE_GAP
Target: <same function/cluster and worker unless replacement is justified>
Unmet acceptance: <claim/evidence/check>
New evidence: <minimal observation/ref>
Scope delta: <usually none>
Required investigation: <specific distinguishing question>
Return: updated local conclusion + evidence + confidence
```

For Luna, extend the input manifest/schema or issue a delta batch instead of resending already processed bulk input.

## Worker result

Normalize results before acceptance or global synthesis:

```text
Task / status / worker profile
Context version and artifact identity/revision
Role intent: bulk-evidence | local-semantics
Input manifest or exact local target
Processed/skipped/error coverage, when bulk
Evidence-index and raw-source references
Local semantic conclusion, when applicable
Confidence and rejected alternatives
Candidate anomalies / contradictions
Accepted or proposed names, types, offsets, states, or schemas
Mutations and validation
New facts and context delta
Risks / unresolved questions
Scope deviation
Recommended next action
Report path
Primary-coordinator decision required, or none
One-paragraph summary
```

Write non-trivial results to a durable report. The lifecycle `worker_done` body is at most three short sentences containing status, coverage/evidence or blocker, and report path. Do not attach bulk raw inputs, full transcripts, complete pseudocode, or copied binaries/databases.

## TaskGraphLite sidecar

Materialize only orchestration facts. Keep absolute tool/database/input locations in the text Task.

```json
{
  "tasks": [
    {
      "id": "L1",
      "role": "luna-max",
      "depends_on": [],
      "read": ["traces/session-a/**"],
      "mutate": ["reports/session-a-index/**"],
      "risk": "low"
    },
    {
      "id": "T1",
      "role": "terra-max",
      "depends_on": ["L1"],
      "read": ["binary/main/functions/decode/**", "reports/session-a-index/decode/**"],
      "mutate": [],
      "risk": "medium"
    }
  ]
}
```

This sidecar does not represent the primary coordinator's global reasoning as a worker Task.

## Global synthesis packet

Give the primary coordinator a compact but drillable packet:

```text
User objective and requested reconstruction
Artifact identities/digests and global context version
Global algorithm/protection hypotheses and accepted vocabulary
Luna input coverage, evidence indexes, anomalies, and raw-source refs
Terra local conclusions with exact target/evidence refs and confidence
Cross-target contradictions and missing evidence
Analysis/database revisions and verified mutations
Requested global decision or final synthesis
```

## Primary coordinator output envelope

Default output is decision-focused; expand when the global reasoning or user needs it.

```text
INITIAL
Global question and requested output
Algorithm/behavior/protection hypotheses
Evidence standard and behavioral oracle
Delegated evidence products and local questions

GATE
Decision: ACCEPT | REVISE | BLOCK
Global model delta or required evidence
Next evidence owner: coordinator | Terra | Luna

FINAL
Algorithm/control/data-flow reconstruction
Protection or anti-analysis findings
Behavior validation
Decisive evidence references
Contradictions and residual uncertainty
```

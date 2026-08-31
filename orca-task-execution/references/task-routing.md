# Task Routing

Load this reference only when the task domain, direct exception, decomposition, batching, or parallel safety is unclear or changes during execution.

## Classify by deliverable

Choose the domain from the result being produced:

- `software`: source/test/build/package changes, migrations, implementation, behavior repair, or code review.
- `reverse`: evidence indexes, bounded local semantics, algorithm/control/data-flow reconstruction, or analysis annotations.
- `mixed`: the user outcome needs both domains. Keep one Run but split worker Tasks at the evidence-to-implementation boundary; each Task declares only `software` or `reverse`.

Tools do not determine ownership. A `bn` lookup feeding a code fix may be a reverse evidence Task followed by a software Task. Using `bn` to edit plugin Python remains software. TDD, profiling, formal verification, or a decompiler can constrain a Task but never own it.

## Direct exception

Direct primary-coordinator execution is allowed only when all are true:

- the requested output and acceptance oracle are unambiguous;
- bounded reconnaissance identifies one exact target and decision;
- the work is semantically small with no unresolved root-cause, contract, security, concurrency, migration, data-integrity, or global-model decision;
- one focused validation path can establish completion;
- delegation would cost at least as much context preparation as execution.

For reverse work, a direct lookup is read-only with one target, one question, and one clear evidence path. Globally coupled algorithm, behavior, or protection synthesis may remain coordinator-owned, but bulk evidence and independently falsifiable local targets should be routed separately.

Direct execution is not sticky. Before the next inspection or mutation, revoke and re-route when any occurs:

- scope crosses the originally recorded targets, symbols, files, artifacts, or evidence ranges;
- the focused reproduction does not settle root cause;
- a second independent failure, target, artifact, hypothesis, or case appears;
- a corpus scan, batch driver, repeated run, multi-case validation, or broad evidence pass is needed;
- software work becomes cross-module or reverse work becomes mutable;
- context compaction or restart leaves the direct basis unproven.

Coordinator-initiated expansion is a new routing event, not permission to preserve direct ownership. Record the new route before continuing.

## Choose worker shape

- One Terra Task when discovery, semantic reasoning, implementation/investigation, validation, and ordinary repair share one mental model.
- One Luna Task when inputs, schema/interfaces, item set, and acceptance are frozen and batch or mechanical work dominates.
- Multiple Tasks only for independently acceptable outcomes with stable interfaces, satisfied dependencies, non-overlapping mutable state, and independent validation.

Pay broad discovery once. Keep a compact Run Context and per-Terra lane/target manifest; pass references and deltas rather than transcripts or repeated repository/binary discovery.

## Mixed Run boundary

Reverse Tasks return cited evidence or bounded conclusions. Software Tasks consume only accepted evidence and own source/test/build changes. If a worker discovers that completion crosses domains, it returns `NEED_DOMAIN_SPLIT` with the exact proposed output boundary; only the primary coordinator creates the new Task.

Do not assign `mixed` to a worker, let one Task load both domain contracts, or use a tool skill as the bridge owner.

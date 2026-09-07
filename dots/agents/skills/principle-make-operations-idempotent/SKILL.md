---
name: principle-make-operations-idempotent
description: "Apply when designing commands, lifecycle steps, or processing loops that run amid crashes, restarts, and retries. Converge to the same end state regardless of partial prior runs."
---

# Make Operations Idempotent

For operations that can be retried, replayed, resumed, or restarted after partial failure, design them to converge to the correct state regardless of how many times they run or where they start from. Do not impose idempotency on deliberately one-shot operations whose contract rejects repetition.

**Why:** Commands, lifecycle operations, and processing loops run where crashes, restarts, and retries are normal. If partial state changes the next run's outcome, every restart becomes a debugging session.

**Possible patterns:**
- Convergent startup: scan for existing state, clean stale artifacts, adopt live sessions
- Content-based cleanup: compare by content equivalence, not creation order
- Self-healing locks: use PID-based stale lock detection
- Idempotent scheduling: failed work respawns cleanly, fresh input regenerated after each cycle

**The test:**
1. What happens if this runs twice in a row?
2. What happens if the previous run crashed at every possible point?
3. Does re-execution converge to the same end state?

If an operation is expected to tolerate replay and an answer depends on partial state, add a reconciliation step or make the non-retryable contract explicit.

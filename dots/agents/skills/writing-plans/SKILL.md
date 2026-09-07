---
name: writing-plans
description: Use when the user explicitly requests an implementation plan, supplies an approved specification for planning, or authorized work spans multiple dependent phases that need separate ownership and verification. Do not use when the contract is already clear and the work can be completed safely as one coherent change.
---

# Writing Plans

## Overview

Write self-contained implementation plans that a skilled engineer or agent can execute without prior project context.

A plan should define outcomes, ownership, constraints, evidence, and replan conditions. It should give the implementer enough structure to proceed safely while leaving room to adapt to the actual codebase.

Do not create a plan merely because implementation has several steps. If the contract is already derivable from the request and repository, proceed with the authorized work. Use a plan when coordination, sequencing, risk, or a durable handoff makes it useful.

When a saved plan is useful, default to `docs/plans/YYYY-MM-DD-<feature-name>.md`.

User or repo preferences override this default.

## When to skip

Skip plan creation when:

- the user requested implementation rather than planning and the contract is already clear
- the change is narrow enough to implement and verify as one coherent unit
- an existing approved plan already covers the work
- the task is diagnosis, review, explanation, or a mechanical operation

Ask a question only when missing information materially changes the contract and cannot be discovered from the repository or supplied context.

## Core Principle

An implementation plan defines the contract for the work.

Each task must make clear:

- what outcome it produces
- which files or modules it owns
- what behavior changes
- what behavior must be preserved
- how success is verified
- what conditions require replanning

Use exact snippets only when the exact shape is part of the contract, such as public API signatures, schemas, migrations, config, expected outputs, protocol examples, state machines, or fragile command sequences.

## Before Writing Tasks

Read the spec and relevant repo context first.

Check for:

- repo-local instructions such as `AGENTS.md`, `CONTRIBUTING`, docs, scripts, or existing plan conventions
- existing architecture and ownership boundaries
- relevant tests and verification commands
- package/project membership rules
- commit, branch, PR, or release policies
- prior specs, ADRs, or task trackers that constrain scope

Promote relevant local constraints into the plan. Do not hardcode project-specific rules in this skill.

## Scope Check

If the spec covers multiple independent subsystems, suggest splitting it into separate plans. Each plan should produce working, testable software on its own.

Make exclusions explicit. A good plan says what it will not do.

## Repo Reconciliation

While drafting the plan, confirm the repo facts that the plan depends on.

Check:

- the named files and modules exist or should be created
- current APIs, initializers, command surfaces, and test seams match assumptions
- existing lifecycle, persistence, routing, or cleanup helpers
- test target membership and command recipes
- generated project or build-system requirements

When the plan names existing APIs, files, commands, or test selectors, distinguish verified facts from preferred implementation shapes. If something was not just verified from the repo, label it as provisional or adaptable.

Repo reconciliation should include only facts that are current, task-relevant, and useful for execution. Do not include provenance notes, prior draft references, requested output filenames, comparison context, or how the plan was generated.

If repo evidence contradicts an assumption, update the task contracts before saving the plan.

## File / Ownership Map

Before tasks, map files and responsibilities.

For each file or module, state whether it is:

- create
- modify
- test
- generated/config
- discovery target

Prefer ownership language over premature line-level edits.

Example:

```markdown
- Modify: `src/session/SessionStore.ts`
  Owns atomic read/write/reset of session rows.
- Test: `tests/session/session-store.test.ts`
  Proves replacement, rollback, and reset behavior.
- Discovery: `src/db/migrations/`
  Confirm existing migration style before adding schema work.
```

## Snippet Rule

Use exact snippets only when the snippet is part of the contract.

Good uses:

- public API signatures
- schema, migration, config, or protocol shape
- expected test names, assertions, fixtures, or golden outputs
- state-machine examples
- wire formats
- fragile command sequences
- small input/output examples

Future test selectors, helper names, and proposed APIs are preferred shapes unless verified from existing source or required by the spec.

If a signature, helper name, test selector, or file shape is only a likely direction, label it as adaptable:

```markdown
Preferred shape; adapt to existing repo conventions if they differ.
```

Do not present speculative APIs as confirmed repo facts.

## Dangerous Operations

For destructive, irreversible, or externally visible operations, require extra proof.

Examples:

- deletion
- reset
- migration
- process shutdown
- payment/auth changes
- data export/import
- external service writes
- filesystem cleanup

Plans must define:

- preflight checks
- blocking/refusal behavior
- what remains unchanged when the operation is blocked, refused, or fails
- rollback or recovery expectations
- idempotency expectations where relevant
- audit/log/trace requirements where relevant
- evidence that proves the blocked/refused/failed path is safe

## Observability Requirements

If the spec requires logs, traces, metrics, audit events, notifications, or other observability behavior, include a dedicated task or explicit evidence step for it.

Do not leave observability requirements only in the architecture summary.

## Task Shape

Use demoable or testable slices. A task should leave the system in a coherent state when executed.

```markdown
### Task N: [Demoable Slice]

**Goal:** What exists after this task.

**Files / Ownership:**

- Create: `path/to/new-file`
- Modify: `path/to/existing-file`
- Test: `path/to/test-file`
- Discovery: `path/to/check-first`

**Contract Delta:**

- Behavior added or changed.
- Behavior preserved.
- Edge cases and invariants.
- Explicit non-goals.

**Required Evidence:**

- Test command or runtime check.
- Expected failing evidence before the implementation step, when practical.
- Expected passing evidence after the implementation step.
- Any logs, traces, screenshots, HTTP responses, database rows, or artifact checks needed.

**Implementation Guidance:**

- Default approach.
- Existing patterns to follow.
- Known constraints.

**Allowed Freedom:**

- Decisions the implementer may make while preserving the contract.

**Do Not Change:**

- Boundaries, behaviors, files, APIs, or user-visible surfaces that must remain untouched.

**Replan If:**

- Conditions that invalidate the task assumptions.
```

## Verification

Every task needs concrete evidence.

Prefer automated tests. If automated tests are not enough, name the smallest runtime or inspection evidence that proves the behavior.

Good evidence examples:

- focused test command and expected result
- lint/typecheck/build command
- HTTP request and expected status/body
- database row count or query result
- trace/log event with required fields
- screenshot or browser evidence for visual work
- diff inspection for generated files or config

Do not write “run tests” without naming relevant tests or commands.

The final verification section must gather every acceptance-critical check in one place. Do not rely only on earlier task-local evidence for requirements that define completion.

When final verification includes source scans for excluded work, scope the scans to relevant production, test, and configuration paths so expected docs/spec mentions do not create false positives.

## Local Command Policy

Plans must incorporate repo-specific command rules discovered from local instructions.

Examples of local command policy can include:

- package manager commands
- test selectors
- build flags
- generated-project steps
- sandbox/elevation requirements
- artifact cleanup rules
- commit restrictions

Do not make these universal in the skill. Make the plan reflect the current repo.

## No Placeholders

These are plan failures:

- `TBD`, `TODO`, `implement later`, `fill in details`
- “add appropriate error handling”
- “handle edge cases”
- “write tests for this”
- “similar to previous task”
- vague verbs without observable behavior
- test steps without commands or expected evidence
- invented APIs presented as confirmed repo facts
- destructive steps without failure/rollback behavior
- broad refactors not required by the spec
- execution-option prompts, “plan saved” prose, or assistant handoff text inside the saved plan document
- provenance notes, prior draft references, requested output filenames, comparison context, or generation-process notes inside the saved plan document

## Plan Header

Every plan should start with:

```markdown
# [Feature Name] Implementation Plan

> **For agentic workers:** Execute this plan task-by-task. Keep each task passing before moving to the next one.

**Goal:** [One sentence describing what this builds]

**Architecture:** [2-3 sentences about the approach]

**Tech Stack:** [Key technologies/libraries/tools]

**Source Spec:** [Path or link]

---
```

## Self-Review

After writing the plan, review it before presenting it.

Check:

1. **Spec coverage:** Every requirement maps to a task or explicit non-goal.
2. **Scope discipline:** The plan does not implement excluded work.
3. **Repo constraints:** Local command, test, build, and git policies are reflected.
4. **Contract clarity:** Each task states behavior, invariants, evidence, and replan triggers.
5. **Snippet necessity:** Exact snippets are only used when contractual.
6. **Stale API risk:** Speculative names, signatures, selectors, or files are marked as adaptable.
7. **Dangerous operations:** Destructive work has preflight, blocked/failure behavior, unchanged-state expectations, and evidence.
8. **Observability:** Required logs, traces, metrics, audits, notifications, or events have tasks or explicit evidence.
9. **Boundary preservation:** Existing dependency direction and module boundaries are preserved unless the spec explicitly changes them.
10. **Task ordering:** Tasks avoid long compile-broken gaps where possible.
11. **Final verification:** Completion-defining checks are gathered in one final verification section.
12. **Source scans:** Excluded-work scans are scoped to relevant paths to avoid expected docs/spec matches.
13. **Placeholder scan:** Remove vague filler and unverifiable claims.
14. **Plan artifact cleanliness:** The saved plan does not include assistant handoff prose, execution-option prompts, provenance notes, prior draft references, requested output filenames, comparison context, or generation-process notes.

Fix issues inline.

## Handoff

If the user requested only a plan, provide the saved plan and stop. Do not automatically ask them to choose an execution mode.

If the request also authorizes implementation, continue only when the approved scope and current environment make the next action clear. Ask about execution strategy only when the choice materially affects ownership, isolation, cost, or risk.

Do not put assistant handoff prose inside the saved plan document. Never commit the plan unless the user explicitly requests a commit.

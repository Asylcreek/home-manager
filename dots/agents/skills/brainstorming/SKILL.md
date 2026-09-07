---
name: brainstorming
description: Use when the user explicitly asks to brainstorm, compare designs, or explore product or architecture choices, or when an unresolved decision would materially change the result. Do not use when the requested contract is already clear from the request, repository, or approved specification.
---

# Brainstorming

Resolve material design uncertainty before implementation. Scale the discussion to the decision instead of making every change pass through a full design process.

## When to skip

Skip brainstorming when:

- the implementation contract is already clear
- repository evidence settles the apparent question
- the user supplied an approved specification or explicit direction
- the remaining choices are local, reversible implementation details
- the task is diagnosis, review, explanation, or mechanical execution

Proceed with the requested work in those cases.

## Workflow

1. **Ground the discussion.** Inspect the relevant repository, documentation, recent changes, and existing patterns before proposing a design. Do not ask for information that is already available.
2. **Isolate material uncertainty.** Identify choices that change product behavior, public contracts, data ownership, security, persistence, or architecture. Treat ordinary implementation details as agent-owned decisions.
3. **Ask only necessary questions.** Ask one concise question when the answer cannot be discovered and a reasonable assumption would materially change the result. Otherwise state the assumption and continue.
4. **Recommend a direction.** Lead with one concrete recommendation and its reasoning. Include alternatives only when they materially differ in risk, cost, behavior, or reversibility.
5. **Present a proportional design.** A small change may need a paragraph. Larger work may need sections for boundaries, data flow, failure behavior, verification, and explicit non-goals.
6. **Request approval only where it matters.** Pause for unresolved product direction, public contracts, irreversible choices, or major architecture. Do not require approval for a direction the user already supplied.

For a brainstorming-only request, stop after the agreed design. For an implementation request, continue once the material choices are settled and the requested scope authorizes implementation.

## Design quality

- Follow existing project patterns unless evidence supports changing them.
- Prefer the smallest design that satisfies the goal.
- Keep responsibilities and dependency direction clear.
- Include targeted cleanup only when it is necessary for the requested behavior.
- Name assumptions, risks, and intentionally deferred work.
- Define evidence that can prove the resulting behavior.

## Artifacts and handoff

Write a durable design document only when the user requests one or the work is substantial enough that later implementation needs a stable contract. Use the repository's established location; otherwise use `docs/specs/YYYY-MM-DD-<topic>-design.md`.

Never commit a design document unless the user explicitly requests a commit.

Use `writing-plans` only when the user asks for an implementation plan or the approved work spans multiple dependent phases that need separate ownership and verification. Otherwise proceed directly within the authorized scope.

## Visual companion

Offer the visual companion only when mockups, diagrams, or side-by-side visual options would make a material decision easier. Ask before opening a local browser experience. If accepted, read `visual-companion.md`; otherwise continue in text.

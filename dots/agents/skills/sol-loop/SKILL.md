---
name: sol-loop
description: Use when asked for a sol loop or independent Sol review.
---

Use GPT-6.1 Sol as an independent reviewer. The implementing agent
owns diagnosis, fixes, and verification.

## Defaults

- Model: GPT-6.1 Sol.
- Reasoning: Medium. Use Standard speed.
- One reviewer per round. The reviewer must not delegate.
- At most 3 rounds, stopping earlier when the change is approved.
- Do not switch models, increase effort, or extend the budget silently.
- Do not commit, push, merge, or post externally through this skill.

## Establish scope

1. Read applicable repository instructions and run `git status --short`.
2. Identify the intended behavior, review paths, and comparison base.
   For a branch, use its merge base with the intended target branch.
   For uncommitted changes only, use HEAD.
3. Include scoped untracked files. Preserve unrelated work.
   Ask only if the intended scope cannot be determined safely.
4. Run relevant checks. Record failures and verification gaps.
5. Prepare a short brief: repository, base SHA, paths, intent,
   acceptance criteria, and check results.

Do not send the entire conversation. Give the reviewer enough context
to inspect the change independently.

## Choose the execution route

### T3 Code

When T3 orchestration tools are available:

- Inspect `orchestrator_capabilities`.
- Resolve GPT-6.1 Sol from the advertised models.
- Use `delegate_task` with review role and async mode, following its
  actual schema. Request Medium and Standard when supported.
- Verify the reviewer can read the checkout containing the changes,
  including uncommitted and untracked files.
- Save the task ID and wait through the available completion mechanism.
- Use a fresh review task for each round, carrying the brief and ledger.

If native delegation cannot run the requested model or inspect the
actual changes, use the CLI route if available.

### Terminal / CLI fallback

Run Codex from the same repository checkout:

```sh
codex exec \
  --model gpt-6.1-sol \
  --sandbox read-only \
  -c model_reasoning_effort=medium \
  -c service_tier=default \
  -
```

Supply the assembled review brief and reviewer instructions through
stdin. Capture the final response and exit status. Use the shell tool's
background execution support when needed, then wait for completion.

Do not alter global Codex configuration or authentication.
If neither route works, report the blocker. Do not substitute a model.

## Reviewer instructions

Include these instructions with every review brief:

Review only. Do not edit files, commit, push, post comments, or delegate.

Inspect the scoped diff, untracked files, surrounding code, and relevant
callers. Prioritize correctness in the intended user scenario.

For each finding, provide:

- Stable ID and severity: blocker, should-fix, or nit.
- File and line.
- Concrete trigger, consequence, and supporting evidence.
- Smallest reasonable correction.

Distinguish observations from hypotheses. Do not demand abstractions,
defensive code, or speculative optimizations without a concrete need.
A serious regression in a caller remains relevant even outside the
changed files.

Return APPROVE, CHANGES, or INCOMPLETE, followed by findings and any
material verification gaps. Keep the response concise.

## Evaluate and fix

- Verify every finding independently. Do not accept it just because Sol
  reported it.
- Before changing code, establish whether the cause is code, config,
  stale state, data, or workflow.
- Fix confirmed issues with the smallest appropriate change.
- Push back with evidence when a finding is incorrect or unnecessary.
- Track findings in a short ledger: ID, status, reason, evidence.
- Re-run checks affected by the fixes.
- Do not edit scoped files while a reviewer is inspecting them.

## Follow-up rounds

Request another round only when behavior changed or a substantive
finding remains unresolved.

Send the original scope, the ledger, check results, and changes since
the previous round. Ask the reviewer to focus on open findings and
changed behavior, including affected callers.

Do not repeat a full audit or rerun unchanged checks without a reason.
Nits and wording-only changes do not require another round.

## Stop and report

Finish when the current behavior diff is approved and no substantive
finding or concern of your own remains.

If the budget ends, findings remain disputed, or review fails, report
the unresolved state. Timeout, silence, and budget exhaustion are not
approval.

Report briefly:

- Model, effort, execution route, and rounds actually used.
- Confirmed fixes and declined findings.
- Verification results and remaining gaps.
- Usage only when exposed; never estimate subscription consumption.

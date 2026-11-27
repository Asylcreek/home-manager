---
name: orchestrate
description: Use when asked to orchestrate work or act as a conductor directing subagents to write, test, review, and integrate changes across one or more slices.
---

Act as the conductor, not the primary coder. You own architecture,
decomposition, contracts, worker briefs, integration, verification,
commits, and durable progress state. Your subagents own bounded
implementation, verbose test runs, independent review, and GUI checks.

Skip fan-out if the job is a tiny single-file fix or early exploratory
debugging where the root cause is unknown. Work directly or use one
focused worker until the shape of the work is clear.

## Defaults

All defaults can be overridden by the user's prompt.

- **Code writers:** GPT-6.2 Sol, Medium reasoning, Standard speed.
- **Review gate:** Use `sol-loop` by default after each major
  integrated slice or risky boundary, and once over the full branch
  diff before finishing.
- **Test and build runners:** Delegate slow builds and verbose test
  suites to a worker that returns pass/fail counts and exact failing
  output, keeping raw logs out of conductor context.
- **GUI, browser, and device tests:** Use `sol-computer-use` for
  desktop apps, `preview_*` or `agent-browser` for web pages, and
  `device_*` for mobile simulators.
- **Durable memory:** Post progress checkpoints to the active Kaneo
  task via `kaneo` or to basic-memory via `remember` when one is
  referenced or relevant. If neither is in play, rely on clean git
  commits and a short local progress note instead of creating tracker
  items unasked.
- **No silent swaps.** If a requested model or route is unavailable,
  report the blocker. Do not substitute another model silently.

## Execution routing

Pick the route that matches your current environment and target.

### T3 Code

- Call `orchestrator_capabilities` once to resolve advertised
  providers, models, and options.
- Use `delegate_task` for another provider's model, custom options,
  isolated checkouts with `isolation: "worktree"`, or linked remote
  machines using `target.environmentId` from `t3_environment_links`.
- Never create a child's worktree in the shell when `delegate_task`
  manages isolation.
- Use native subagents only for same-provider work that needs no extra
  options or separate checkout.

### Outside T3 Code

- Use your native subagent tool when it supports the requested model
  and isolation.
- For GPT-6.2 Sol over CLI, run from the target checkout or worktree:

```sh
codex exec \
  --model gpt-6.2-sol \
  -c model_reasoning_effort=medium \
  -c service_tier=default \
  -
```

Supply the brief through stdin. Do not alter global CLI config or auth.

### Remote machines

When work spans machines, check `hostname`, `fleet`, and linked
environments. If SSH hits interactive, keychain, GUI, or code-signing
walls like macOS Xcode signing, delegate directly to an agent on that
remote machine instead of fighting SSH restrictions.

## Preflight

1. Read repository instructions like `AGENTS.md` or `CLAUDE.md`, plus
   the relevant plan or task.
2. Run `git status --short` and check the current branch.
3. Never implement on `main` or `master` without explicit user consent.
   Create or verify a dedicated task branch before dispatching writers.
4. Note any environment constraints such as isolated debug builds,
   remote test targets, or production services that must stay untouched.
5. Start work without asking "are we ready?". Ask the user only if an
   unresolved ambiguity would materially change the outcome.

## Decomposition and parallelism

- **Land contracts first.** Before fanning out parallel writers, commit
  shared types, schemas, interfaces, or API signatures first, or
  assign strictly disjoint files to each writer.
- **Parallel lane for isolated state.** Run independent coding slices,
  builds with separate output or derived-data directories, and pure
  unit tests concurrently in separate worktrees.
- **Serial lane for shared state.** Serialize anything competing for a
  shared resource: merges to the task branch, fixed ports, shared
  databases, debug app launches, desktop GUI focus, simulators, and
  remote test hosts.
- **Protect production.** Never overwrite, restart, or point tests at
  production binaries, live services, or live user data directories.
  Use isolated build outputs and temporary data dirs.

## Conductor and worker boundaries

**Conductor owns:**

- Breaking work into slices and sequencing waves.
- Writing self-contained briefs.
- Integrating worktree branches onto the task branch and resolving
  merge conflicts.
- Small glue edits and trivial 1 to 5 line review fixes. Do not spin up
  a writer for a two-line nit.
- Verifying the merged branch, running reviews, and updating durable
  memory.

**Workers own:**

- Bounded implementation within their assigned files and contract.
- Running slice-level builds and tests before reporting back.
- Committing verified changes on their worktree branch before handback.
- Verbose test execution, code review, or GUI inspection when assigned.

Workers start with no conversation history. Every brief must include:

- Goal and where this slice fits in the larger change.
- Exact files or symbols in scope, plus explicit non-goals and files
  the worker must not edit.
- Interface contract and base SHA or branch.
- Verification commands to run before committing and reporting back.
- Instruction not to delegate or spawn subagents.
- Required return format: status of `DONE`, `DONE_WITH_CONCERNS`,
  `NEEDS_CONTEXT`, or `BLOCKED`; commit SHAs and changed files; exact
  commands run and their results; and any newly discovered issues.

## Integration, review, and commits

1. Inspect each writer's commits, then merge or cherry-pick completed
   slices onto the task branch and resolve conflicts.
2. Run integrated checks after merging. Isolated worktree passes do not
   prove the combined branch works.
3. Keep the task branch at clean, verified milestones. Commit conductor
   glue fixes or conflict resolutions cleanly, and never land
   known-broken state onto the task branch.
4. Run `sol-loop` after each major integrated slice or risky boundary,
   and run a final `sol-loop` over the full branch diff before
   handback. Verify every finding yourself before fixing or pushing
   back.
5. For GUI tests, inspect returned screenshots yourself before claiming
   success.

## Discovered issues

Workers must report newly discovered bugs or gaps to the conductor
rather than filing tickets directly. Triage every finding into one of
two buckets:

- **Blocking or in-scope.** Add it to the active work queue, fix it in
  this run, and note it in the current task.
- **Out-of-scope or pre-existing.** File a separate issue via `kaneo`
  or the project tracker with enough context for a future run. Do not
  pull it into the current branch unless the user asked to fix
  everything found. List filed issues in the final report.

## Durable checkpoints and flow

Post short checkpoints to the active Kaneo task or basic-memory note
after slicing the plan, after merging a milestone, on scope changes or
blockers, and at completion. Include only:

- Completed slices and commit SHAs.
- Active worktrees or branches.
- Filed follow-up issues.
- Open blockers and the next step.

Never dump raw logs or full transcripts into checkpoints.

Keep executing across slices without pausing to ask whether to
continue. Stop and escalate to the user only when:

- A product or design question materially changes user-visible
  behavior.
- An action risks production state, destructive changes, or requires
  credentials or approvals you do not have.
- A slice stays blocked after two distinct attempts such as better
  context, a smaller split, or a stronger model.

## Cleanup and handback

1. Remove temporary worktrees, scratch build or data directories, and
   background processes you started, or report any intentionally left
   running.
2. Run final verification on the integrated branch.
3. Report concisely:
   - Branch, commits, and completed slices.
   - Review summary from `sol-loop`, including declined findings.
   - Verification results and any remaining gaps.
   - Follow-up issues filed and any unresolved blockers.

**Important:** NEVER assume, if you do not know, ask questions or research online ... DO NOT ASSUME

1. If you are not a vision-model, you have mcps to help you see
2. Code you write is supposed to be self-documenting, if you feel the need to add a comment, you should rewrite the code instead.

## Operating Principles

### Evidence Before Reasoning
When behavior can be observed directly, prefer evidence over code-only reasoning.

- Use logs, traces, screenshots, tests, runtime inspection, and reproduction before concluding.
- For UX, performance, scrolling, rendering, timing, and state-restore issues, prioritize runtime evidence.
- If confidence is not high, say so and gather more evidence.

### Facts vs Hypotheses
Never present a guess as a conclusion.

- State observations as facts.
- State explanations as hypotheses until verified.
- Resolve ambiguity before proposing major fixes.

### Validate Real Behavior
Code that looks correct is not enough.

- Verify changes in the user’s actual scenario whenever possible.
- Treat user-reported interaction quality as a real acceptance signal.
- If something is technically correct but still feels wrong, treat it as unresolved.

### Small, Reversible Steps
Prefer incremental, testable changes over broad speculative rewrites.

- Make the smallest change that tests the current hypothesis.
- Revalidate after each meaningful change.
- If experimentation increases uncertainty, revert to the last stable state.

### Preserve Stable Checkpoints
Keep stable behavior distinct from experiments.

- Maintain recoverable known-good states.
- If the user pauses or tables a problem, return to the last stable version of that work.
- Do not leave half-integrated experiments unless explicitly requested.

### Scope Discipline
Do not expand work beyond the requested scope.

- Limit cleanup and refactors to code directly involved in the task unless asked otherwise.
- Separate required work from optional improvements.

### Prefer Concrete Recommendations
When asked what to do next, give one clear recommendation by default.

- Prefer a concrete plan over a list of loose options.
- Include alternatives only when they materially affect risk, cost, or correctness.

### Be Falsifiable
Communicate in verifiable terms.

- Prefer: “the logs show…”, “this test confirms…”, “this is still a hypothesis…”, “this improved X but regressed Y…”
- Avoid declaring success when only part of the problem is solved.

### Respect User Signals
Treat the user’s direct observations as important evidence.

- If the user says something feels wrong, incorporate that into diagnosis.
- If user feedback conflicts with your model, update your model.

### Report Status Clearly
When reporting back, distinguish between:

- confirmed working
- improved but incomplete
- unresolved
- intentionally deferred

## Git Commits

**CRITICAL** NEVER COMMIT UNLESS EXPLICITY REQUESTED TO

**Use conventional commit format for all git commits.**

Format: `<type>(<scope>): <description>` with types like feat, fix, chore, docs, style, refactor, perf, test, build.

Key rules:

- Use lowercase for type and scope
- Keep description under 72 characters
- Use imperative mood ("add" not "added")
- No Co-Authored-By footer unless requested

→ See [docs-rules/git-commits.md](~/.agents/docs-rules/git-commits.md) for types, examples, and complete rules

## Pull Request Guidelines

**Keep PR bodies clean without AI attribution or branding.**

Never add "Generated with Droid/Claude/Codex" footers or any AI attribution to pull request descriptions.

Key rules:

- No "Generated with [Droid](...)" footers
- No AI attribution or branding
- Use an empty body unless otherwise stated by the user, else focus on: summary
- Use HEREDOC for clean formatting
- **CRITICAL: Never use --squash flag when merging PRs unless explicitly requested by the user. Use standard merge instead.**
- **ALWAYS: Add user (@me) as assignee when creating PRs using --assignee @me**
- **ALWAYS: Use --label enhancement for PRs unless otherwise specified by the user**
- Use `--delete-branch` option when asked to delete a merge a PR and delete its branch with `gh` cli tool.
- Use `--body ""` option when the pr body is empty and you are creating a pr with the `gh` cli tool.

→ See [docs-rules/pull-requests.md](~/.agents/docs-rules/pull-requests.md) for complete PR guidelines

## File Reading Efficiency

**CRITICAL: Minimize token usage by avoiding redundant file reads.**

Never re-read files that were already read in the conversation. Reference from context instead.

Key rules:

- Never re-read files already read in this conversation
- Reference from conversation history when possible
- Batch multiple file reads in parallel
- Check if file was already read before reading

Exceptions: user explicitly asks, file was modified, or verifying recent changes.

→ See [docs-rules/file-reading-efficiency.md](~/.agents/docs-rules/file-reading-efficiency.md) for complete rules and examples

## Generic NestJS Patterns

**Comprehensive patterns for any NestJS project.**

These patterns guide implementation when writing or editing NestJS code, covering modules, controllers, services, testing, security, and more.

Key areas covered:

- Module/Feature organization and structure
- DTO, Service, Controller patterns
- Testing and error handling
- Guards, decorators, pipes, interceptors
- Dependency injection and best practices

→ See [docs-rules/nestjs-patterns/index.md](~/.agents/docs-rules/nestjs-patterns/index.md) for complete NestJS patterns documentation

@RTK.md

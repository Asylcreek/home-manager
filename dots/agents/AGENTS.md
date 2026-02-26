**Important:** NEVER assume, if you do not know, ask questions or research online ... DO NOT ASSUME

1. If you are not a vision-model, you have mcps to help you see
2. Code you write is supposed to be self-documenting, if you feel the need to add a comment, you should rewrite the code instead.

## Git Commits

**CRITICAL** NEVER COMMIT UNLESS EXPLICITY REQUESTED TO

**Use conventional commit format for all git commits.**

Format: `<type>(<scope>): <description>` with types like feat, fix, chore, docs, style, refactor, perf, test, build.

Key rules:

- Use lowercase for type and scope
- Keep description under 72 characters
- Use imperative mood ("add" not "added")
- No Co-Authored-By footer unless requested

→ See [rules/git-commits.md](.factory/rules/git-commits.md) for types, examples, and complete rules

## Pull Request Guidelines

**Keep PR bodies clean without AI attribution or branding.**

Never add "Generated with Droid/Claude/Codex" footers or any AI attribution to pull request descriptions.

Key rules:

- No "Generated with [Droid](...)" footers
- No AI attribution or branding
- Focus on: summary, test plan, and relevant context
- Use HEREDOC for clean formatting
- **CRITICAL: Never use --squash flag when merging PRs unless explicitly requested by the user. Use standard merge instead.**
- **ALWAYS: Add user (@me) as assignee when creating PRs using --assignee @me**
- **ALWAYS: Use --label enhancement for PRs unless otherwise specified by the user**
- Use `--delete-branch` option when asked to delete a merge a PR and delete its branch with `gh` cli tool.
- Use `--body ""` option when the pr body is empty and you are creating a pr with the `gh` cli tool.

→ See [rules/pull-requests.md](.factory/rules/pull-requests.md) for complete PR guidelines

## File Reading Efficiency

**CRITICAL: Minimize token usage by avoiding redundant file reads.**

Never re-read files that were already read in the conversation. Reference from context instead.

Key rules:

- Never re-read files already read in this conversation
- Reference from conversation history when possible
- Batch multiple file reads in parallel
- Check if file was already read before reading

Exceptions: user explicitly asks, file was modified, or verifying recent changes.

→ See [rules/file-reading-efficiency.md](.factory/rules/file-reading-efficiency.md) for complete rules and examples

## Generic NestJS Patterns

**Comprehensive patterns for any NestJS project.**

These patterns guide implementation when writing or editing NestJS code, covering modules, controllers, services, testing, security, and more.

Key areas covered:

- Module/Feature organization and structure
- DTO, Service, Controller patterns
- Testing and error handling
- Guards, decorators, pipes, interceptors
- Dependency injection and best practices

→ See [rules/nestjs-patterns/index.md](.factory/rules/nestjs-patterns/index.md) for complete NestJS patterns documentation

@RTK.md

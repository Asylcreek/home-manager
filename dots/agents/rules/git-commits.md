# Git Commits - Use Conventional Commit Style

**ALWAYS use conventional commit format** when creating git commits.

## Format

```
<type>(<scope>): <description>

[optional body]
```

## Types

- `feat` - new feature
- `fix` - bug fix
- `chore` - maintenance tasks
- `docs` - documentation changes
- `style` - formatting, missing semi colons, etc.
- `refactor` - refactoring code
- `perf` - performance improvements
- `test` - adding tests
- `build` - build system changes

## Examples

```
feat(auth): add OAuth2 login support

fix(button): remove unused React import

docs(stories): standardize callout format

chore(deps): upgrade peer dependencies to latest versions
```

## Rules

- Use lowercase for type and scope
- Keep description under 72 characters
- Use imperative mood ("add" not "added" or "adds")
- Do NOT add Co-Authored-By footer unless explicitly requested

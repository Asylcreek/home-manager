---
name: review-code-changes
description: Review local code changes, especially uncommitted git changes, by gathering diff evidence and asking reviewer agents to inspect code reuse, code quality, maintainability, correctness risks, and efficiency. Use when the user asks for a code review, review of uncommitted changes, pre-commit review, quality pass, reuse audit, refactor review, or efficiency review.
---

# Review Code Changes

Review actual changed behavior before making recommendations. Treat the diff, runtime evidence, tests, and project conventions as stronger evidence than code-only impressions.

## Workflow

1. Inspect scope with `git status --short`, `git diff --stat`, and staged diff stats.
2. Identify changed files, untracked source files, and likely test files.
3. Read only the files and diffs needed to review the change.
4. Ask independent reviewer agents when available:
   - Reuse reviewer: duplicated logic, missed existing helpers, abstraction fit.
   - Quality reviewer: correctness, maintainability, API boundaries, tests.
   - Efficiency reviewer: unnecessary work, inefficient data access, rendering risks, performance risks.
5. Synthesize findings. Do not blindly merge agent opinions.
6. Report findings first, ordered by severity, with file and line references.
7. Separate confirmed issues from hypotheses.
8. Include test gaps and residual risk.
9. Do not edit files unless the user explicitly asks for fixes.

## Review Standards

Prioritize:

- Bugs and behavioral regressions
- Missed reuse of existing code or patterns
- Overly broad or fragile abstractions
- Inefficient loops, queries, rendering, allocations, or network calls
- Missing validation, error handling, or tests
- Inconsistent project conventions

Avoid:

- Style-only comments unless they affect maintainability
- Speculative rewrites
- Suggesting new abstractions without clear repeated complexity
- Re-reading files already inspected unless they changed

## Agent Prompts

When using reviewer agents, give each agent the same raw evidence and a narrow lens. Do not include expected findings.

Reuse reviewer:

```text
Review these code changes for code reuse and project fit. Look for duplicated logic, missed existing helpers, inconsistent local patterns, unnecessary abstractions, and opportunities to simplify by reusing existing code. Return findings only when they are actionable and supported by file/line evidence.
```

Quality reviewer:

```text
Review these code changes for correctness, maintainability, API boundaries, error handling, and test coverage. Prioritize bugs and behavioral regressions over style preferences. Return findings only when they are actionable and supported by file/line evidence.
```

Efficiency reviewer:

```text
Review these code changes for efficiency and performance risks. Look for unnecessary repeated work, inefficient data access, rendering churn, avoidable allocations, excessive network calls, and scalability issues. Return findings only when they are actionable and supported by file/line evidence.
```

## Output Format

Start with findings.

If issues exist:

- `[P1] Title` with file/line and evidence
- `[P2] Title` with file/line and evidence
- `[P3] Title` with file/line and evidence

Then include:

- Open questions
- Test gaps
- Brief summary

If no issues are found, say so clearly and mention remaining risk.

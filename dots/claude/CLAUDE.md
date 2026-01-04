## Model Selection for Sub-Agents

When using the Task tool to spawn sub-agents, **always use the most cost-effective model** for the task:

### Use `haiku` for:

- Simple file reading or exploration
- Pattern matching and searching
- Listing files or directory structures
- Quick lookups (finding a class, function, or variable)
- Summarizing small amounts of code
- Any task that doesn't require deep reasoning

### Use `sonnet` for:

- Moderate complexity analysis
- Code review of individual files
- Understanding how a feature works
- Most general-purpose exploration tasks

### Use `opus` for:

- Complex architectural decisions
- Multi-step reasoning problems
- Tasks requiring nuanced judgment
- Planning implementations with trade-offs
- Security analysis or subtle bug detection

### Example:

Simple exploration - use haiku

Task(subagent_type="Explore", model="haiku", prompt="Find all React components in src/")

Complex analysis - use opus

Task(subagent_type="Plan", model="opus", prompt="Design the authentication system...")

**Default to `haiku`** unless the task clearly requires deeper reasoning. When in doubt, start with haiku—you can always escalate if needed.

## Sub-Agent Output Handling

When using the Task tool to launch sub-agents (explore, general-purpose, etc.), you MUST present the complete, verbose output from the sub-agent to the user WITHOUT summarizing it.

### Rules:

1. After a sub-agent completes its task, show the FULL output to the user
2. Do NOT create concise summaries of sub-agent results
3. Do NOT condense or paraphrase the sub-agent's findings
4. Present the complete response as returned by the sub-agent
5. You may add brief context (e.g., "Here's what the agent found:") but then show the full output

The user prefers to see all details and findings from sub-agents directly.

## File Reading Efficiency

**CRITICAL**: Minimize token usage by avoiding redundant file reads.

### Rules:

1. **Never re-read a file** that has already been read in this conversation unless the user explicitly asks or the file has been modified
2. **Reference from context**: If information from a previously read file is needed, reference it from the conversation history
3. **Before reading any file**, check if it was already read in this conversation
4. **Batch reads**: If you need to read multiple files, read them all in parallel in a single message
5. **Ask first**: If unsure whether to read a file, ask the user if they want you to read it

### Examples:

❌ **Bad** (wastes tokens):
User: What's in the config file?
Assistant: Let me read it again...
[Reads file that was already read 5 messages ago]

✅ **Good** (efficient):
User: What's in the config file?
Assistant: Based on the config file I read earlier (message #3), it contains...

### Exception:

Only re-read a file if:

- The user explicitly says "re-read" or "read it again"
- You see a system reminder that the file was modified
- You need to verify recent changes you just made

## Gemini CLI Integration

**PRIMARY DIRECTIVE**: Claude Code should use the Gemini CLI to do as much of the thinking and processing as possible. Claude Code should only act as the orchestrator, using as little tokens itself as possible.

### When to Use Gemini CLI

Use `gemini` CLI for heavy computational work:

1. **Large-scale codebase analysis** (50+ files or 100KB+ total)

   - Understanding entire project architecture
   - Mapping package structure across modules
   - Finding all implementations of a pattern

2. **Multi-file context gathering**

   - Analyzing entire directories
   - Understanding how features work across multiple files
   - Identifying coding patterns project-wide

3. **Complex code comprehension**

   - Understanding unfamiliar codebases
   - Verifying feature implementation across the project
   - Deep architectural analysis

4. **Before major operations**
   - Before generating tasks
   - Before creating tests
   - Before refactoring

### Gemini CLI Syntax

**Basic usage:**

```bash
gemini -p "Your prompt here"

# Include files/directories using @ symbol (paths relative to current directory):

# Single file
gemini -p "@src/main.py Explain this file's purpose"

# Multiple files
gemini -p "@package.json @src/index.js Analyze dependencies"

# Entire directory
gemini -p "@src/ Summarize architecture"

# All files in project
gemini --all_files -p "Analyze project structure"

# Common flags:
- -m gemini-2.0-flash-exp - Specify model (1M token context)
- --yolo - Auto-accept all tool actions (non-interactive)
- --all_files - Include all files in analysis

# Example Workflows

# Analyzing a new codebase:

gemini -m gemini-2.0-flash-exp -p "@. Analyze this codebase comprehensively. Identify: 1) Project structure and architecture, 2) Main components and their purposes, 3) Data models with exact field names, 4) Testing patterns, 5) Key dependencies. Provide file paths and specific references."

# Understanding a specific feature:

gemini -p "@src/features/authentication Explain how authentication works in this codebase. Include all related files, data flow, and security patterns."

# Before generating tests:

gemini -p "@src/models @tests Analyze existing test patterns and data models. I need: 1) Exact field names and types for all models, 2) Test naming conventions, 3) Test structure patterns, 4) Mocking patterns used."
```

### Integration Pattern

For large analysis tasks:

1. Check scope first - Count files or estimate complexity
2. Delegate to Gemini - Use gemini CLI for heavy lifting
3. Process results - Extract key insights from Gemini's output
4. Take action - Use the context to perform the user's requested task

Example:

User: "Analyze this codebase and generate tasks"

Step 1: Check scope
→ find . -name "\*.py" | wc -l # Returns 150 files

Step 2: Delegate to Gemini
→ gemini -m gemini-2.0-flash-exp --all_files -p "Analyze this Python codebase..."

Step 3: Process Gemini's output
→ Extract architecture patterns, data models, missing features

Step 4: Generate tasks using context
→ Create specific, actionable tasks based on analysis

### Optimizing Token Usage with Haiku for Gemini Orchestration

**Use haiku model for agents that primarily orchestrate Gemini CLI calls.**

When spawning agents that just run `gemini` commands and pass results back, use `model="haiku"` to minimize token costs:

#### Pattern:

````python
# ❌ Expensive - uses sonnet for simple orchestration
Task(
    subagent_type="general-purpose",
    prompt="Run gemini CLI to analyze the codebase: gemini --all_files -p 'Analyze this project...'"
)

# ✅ Efficient - uses haiku for orchestration
Task(
    subagent_type="general-purpose",
    model="haiku",
    prompt="Run gemini CLI to analyze the codebase: gemini --all_files -p 'Analyze this project...'"
)

When to Use Haiku for Gemini:

Always use haiku when the agent will:
- Execute gemini CLI commands
- Run bash commands to gather file lists
- Pass through gemini's output without analysis
- Save gemini results to files
- Simple orchestration with no reasoning needed

Example workflows:

# Codebase analysis with haiku orchestration
Task(
    subagent_type="general-purpose",
    model="haiku",
    prompt="""
    1. Run: gemini -m gemini-2.0-flash-exp --all_files -p "Analyze this codebase comprehensively..."
    2. Save the output to .claude/context.md
    """
)

# Feature analysis with haiku orchestration
Task(
    subagent_type="general-purpose",
    model="haiku",
    prompt="""
    Run gemini CLI to understand the authentication feature:
    gemini -p "@src/auth Explain how authentication works, include all related files"
    Then report back the findings.
    """
)

Cost Comparison:

Without haiku optimization:
- Sonnet orchestration: ~$3.00/MTok
- Gemini analysis: ~$0.10/MTok (approximate)
- Total: $3.10/MTok for simple pass-through

With haiku optimization:
- Haiku orchestration: ~$0.25/MTok
- Gemini analysis: ~$0.10/MTok
- Total: $0.35/MTok for same result

Savings: ~89% reduction in orchestration costs

When NOT to Use Haiku:

Don't use haiku if the agent needs to:
- Analyze and interpret gemini's output before presenting it
- Make complex decisions based on results
- Perform multi-step reasoning
- Handle error cases with nuanced judgment

In those cases, use sonnet or opus as appropriate.

### Saving Context for Agents

When working with projects that have agents (task-generator, test-generator, etc.), **always save Gemini CLI output** to the project's context file:

**After running Gemini CLI:**

```bash
# Save the context for agents to use
gemini -p "..." > .claude/context.md
````

Or manually save by:

1. Run Gemini CLI analysis
2. Copy the output
3. Write to .claude/context.md in the project root

Why this matters:

- Agents read from .claude/context.md instead of the entire codebase
- Reduces token usage by 90%+ (one small file vs 20+ source files)
- Context persists for the session and can be reused

Standard location: .claude/context.md (project-specific)

Agents that use this file:

- task-generator - reads full context
- test-generator - reads full context

Agents that use git diff instead:

- test-validator - reads only changed test files
- tinstruction-validator - reads only changed files

### When NOT to Use Gemini

Don't use Gemini for:

- Reading 1-5 specific files (use Read tool directly)
- Simple file operations
- Tasks you can complete with existing context
- Follow-up questions about already-analyzed code
- Quick searches or pattern matching (use Grep/Glob instead)

### Benefits

This hybrid approach:

- Reduces Claude Code token usage by 60-80% for large analysis tasks
- Leverages Gemini's 1M token context window for deep codebase understanding
- Allows Claude to focus on orchestration rather than heavy computation
- Mirrors mixture-of-experts architecture using each model's strengths

```

```

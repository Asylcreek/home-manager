## Model Selection for Sub-Agents

When using sub-agents, **always use the most cost-effective model** for the task:

### Use cost-effective/fast models for:

- Simple file reading or exploration
- Pattern matching and searching
- Listing files or directory structures
- Quick lookups (finding a class, function, or variable)
- Summarizing small amounts of code
- Any task that doesn't require deep reasoning

### Use capable models for:

- Moderate complexity analysis
- Code review of individual files
- Understanding how a feature works
- Most general-purpose exploration tasks

### Use powerful models for:

- Complex architectural decisions
- Multi-step reasoning problems
- Tasks requiring nuanced judgment
- Planning implementations with trade-offs
- Security analysis or subtle bug detection

### Example:

Simple exploration - use fast model
@explore Find all React components in src/
Complex analysis - use powerful model
@general Design the authentication system...
**Default to fast/cost-effective models** unless the task clearly requires deeper reasoning. When in doubt, start with a fast model—you can always escalate if needed.

## Sub-Agent Output Handling

When using sub-agents (explore, general-purpose, etc.), you MUST present the complete, verbose output from the sub-agent to the user WITHOUT summarizing it.

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

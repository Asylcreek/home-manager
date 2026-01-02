# Sub-Agent Output Handling

When using the Task tool to launch sub-agents (explore, general-purpose, etc.), you MUST present the complete, verbose output from the sub-agent to the user WITHOUT summarizing it.

## Rules:

1. After a sub-agent completes its task, show the FULL output to the user
2. Do NOT create concise summaries of sub-agent results
3. Do NOT condense or paraphrase the sub-agent's findings
4. Present the complete response as returned by the sub-agent
5. You may add brief context (e.g., "Here's what the agent found:") but then show the full output

The user prefers to see all details and findings from sub-agents directly.

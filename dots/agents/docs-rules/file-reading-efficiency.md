# File Reading Efficiency

**CRITICAL**: Minimize token usage by avoiding redundant file reads.

## Rules

1. **Avoid redundant reads**: Reuse context when it contains the exact information needed
2. **Reference from context**: Use conversation history when it is complete and current
3. **Before reading any file**, check if it was already read in this conversation
4. **Batch reads**: If you need to read multiple files, read them all in parallel in one message
5. **Read targeted sections**: Re-read the relevant sections when available context is incomplete, uncertain, or stale

## Examples

### ❌ **Bad** (redundant read when context is complete and current):
```
User: What's in the config file?
Droid: Let me read it again...
[Reads file that was already read 5 messages ago]
```

### ✅ **Good** (reuse complete, current context):
```
User: What's in the config file?
Droid: Based on the config file I read earlier (message #3), it contains...
```

## When to re-read

Re-reading is appropriate when:

- Available context is incomplete, uncertain, or stale
- The user asks for a re-read
- The file changed
- Current contents need verification

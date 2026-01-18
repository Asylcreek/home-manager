# File Reading Efficiency

**CRITICAL**: Minimize token usage by avoiding redundant file reads.

## Rules

1. **Never re-read a file** that has already been read in this conversation unless the user explicitly asks or the file has been modified
2. **Reference from context**: If information from a previously read file is needed, reference it from the conversation history
3. **Before reading any file**, check if it was already read in this conversation
4. **Batch reads**: If you need to read multiple files, read them all in parallel in one message
5. **Ask first**: If unsure whether to read a file, ask the user if they want you to read it

## Examples

### ❌ **Bad** (wastes tokens):
```
User: What's in the config file?
Droid: Let me read it again...
[Reads file that was already read 5 messages ago]
```

### ✅ **Good** (efficient):
```
User: What's in the config file?
Droid: Based on the config file I read earlier (message #3), it contains...
```

## Exceptions

Only re-read a file if:

- The user explicitly says "re-read" or "read it again"
- You see a system reminder that the file was modified
- You need to verify recent changes you just made

#!/usr/bin/env bash
# Ralph Loop - Iterative Development Orchestrator
# This script initializes the state and then outputs markdown instructions for the AI

set -euo pipefail

# Defaults
MAX_ITERATIONS=10
COMPLETION_PROMISE=""
PROMPT=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --max-iterations)
      if [[ -n "$2" && "$2" =~ ^[0-9]+$ ]]; then
        MAX_ITERATIONS="$2"
        shift 2
      else
        echo "Warning: Invalid --max-iterations value, using default of 10"
        MAX_ITERATIONS=10
        shift
      fi
      ;;
    --completion-promise)
      if [[ -n "$2" ]]; then
        COMPLETION_PROMISE="$2"
        shift 2
      else
        echo "Warning: --completion-promise requires a value, ignoring"
        shift
      fi
      ;;
    *)
      # Everything else is part of the prompt
      PROMPT+="$1 "
      shift
      ;;
  esac
done

# Check if prompt is empty
if [[ -z "$PROMPT" ]]; then
  echo "Error: No task provided"
  echo "Usage: /ralph-loop <task> --max-iterations <n> --completion-promise <text>"
  exit 1
fi

# Create .factory directory if it doesn't exist
mkdir -p .factory

# Create state file
cat > .factory/ralph-loop.local.md <<EOF
---
active: true
iteration: 1
max_iterations: $MAX_ITERATIONS
completion_promise: $(if [[ -n "$COMPLETION_PROMISE" ]]; then echo "\"$COMPLETION_PROMISE\""; else echo "null"; fi)
started_at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$PROMPT
EOF

# Output status
echo "✅ Ralph Loop initialized"
echo ""
echo "Task: $PROMPT"
echo "Max iterations: $MAX_ITERATIONS"
if [[ -n "$COMPLETION_PROMISE" ]]; then
  echo "Completion promise: $COMPLETION_PROMISE"
else
  echo "Completion promise: (none)"
fi
echo ""
echo "State file created at .factory/ralph-loop.local.md"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
cat <<'MARKDOWN'

---
description: Iterative self-referential development loop
argument-hint: "<task> --max-iterations <n> --completion-promise <text>"
---

# Ralph Loop - Iterative Development Orchestrator

The state file has been created by the script above. You are now the orchestrator.

## CRITICAL ORCHESTRATOR RULES

You are the ORCHESTRATOR, NOT a worker. Your job is to manage the loop, verify work, and NEVER do implementation yourself.

1. **NEVER take direct implementation action**
   - You are ORCHESTRATOR, NOT a worker
   - NEVER: Edit, Create files (except for sed to increment iteration)
   - NEVER: Write implementation code yourself
   - ALWAYS: Let sub-droids do the work
   - If max iterations reached without success: STOP and report failure

2. **ALL sub-droids get IDENTICAL prompts**
   - EVERY sub-droid gets: EXACTLY $PROMPT_TEXT
   - NO: "fix this", "try again", "improve that"
   - NO: iteration context, previous attempts, or explanations
   - Sub-droids discover previous work naturally from files/git

3. **Tools you MAY use for verification:**
   - Read, Grep, Glob, LS - to inspect files
   - FetchUrl, WebSearch - to research documentation
   - Execute - ONLY for: sed (iteration counter), reading files
   - Task - ONLY to spawn: sub-droids OR code-reviewer droids
   - These tools help you VERIFY sub-droid work is complete

4. **Tools you MUST NEVER use:**
   - Edit, Create - implementation is for sub-droids only
   - Execute (writing files) - let sub-droids do this

## How It Works

1. **Read state file** to get current iteration and configuration:
   ```bash
   STATE_FILE=".factory/ralph-loop.local.md"
   ITERATION=$(grep '^iteration:' "$STATE_FILE" | sed 's/iteration: *//')
   MAX_ITERATIONS=$(grep '^max_iterations:' "$STATE_FILE" | sed 's/max_iterations: *//')
   COMPLETION_PROMISE=$(grep '^completion_promise:' "$STATE_FILE" | sed 's/completion_promise: *//' | sed 's/^"\(.*\)"$/\1/')
   PROMPT_TEXT=$(awk '/^---$/{i++; next} i>=2' "$STATE_FILE")
   ```

2. **Prepare the sub-droid prompt**:
   - The sub-droid gets ONLY: "$PROMPT_TEXT"
   - Add NOTHING about iterations, previous work, or orchestration
   - The sub-droid should treat this as a fresh prompt each time
   - They will naturally discover previous work in files and git history

3. **Spawn SubDroid** using Task tool:
   - Sub-droid type: `code-architect`
   - Prompt: (just "$PROMPT_TEXT" - nothing more)
   - The sub-droid will work on the task autonomously

4. **After SubDroid completes**:

   **Get the completion promise:**
   - Read COMPLETION_PROMISE from state file
   - This is the value from: --completion-promise flag
   - Example: "COMPLETE", "DONE", "YES", or any string the user specified

   **Check if promise appears in sub-droid output:**
   - Get the sub-droid's complete output
   - Check if COMPLETION_PROMISE string appears exactly in the output
   - Use simple string matching (not regex)

   **If completion promise IS present:**

   - **VERIFY**: Check that all criteria from the user's prompt are met:
     * Read the user's original prompt (PROMPT_TEXT)
     * Identify specific completion criteria mentioned
     * Verify each criterion (use Read, Grep, FetchUrl, WebSearch, etc.)
     * Use code-reviewer droids if task is complex

   - **Decision**:
     * If verification passes: Remove state file, STOP looping
     * If verification fails: Continue to next iteration (don't accept false completion)

   **If completion promise NOT present:**

   - **Decision**:
     * If iteration < max_iterations: Continue to next iteration
     * If iteration >= max_iterations: Remove state file, STOP looping

5. **When continuing:**
   - Increment iteration counter in state file using sed:
     ```bash
     sed -i '' 's/^iteration: [0-9]*$/iteration: '$((ITERATION + 1'))'/' "$STATE_FILE"
     ```
   - Go back to step 2

## Important Notes

- **Clean Prompts**: Sub-droids get ONLY the user's prompt - no iteration context
- **Self-Referential**: Each sub-droid discovers previous work naturally from files/git
- **Inherit Model**: Sub-droids use the same model as you
- **You Track Iterations**: Only the orchestrator knows the iteration count
- **Verify Everything**: Never accept completion without checking actual work is complete
- **Orchestrate Only**: Your role is to spawn sub-droids and verify their work, NOT to do implementation yourself

## Current Iteration: 0

**Start now by reading the state file and spawning the first SubDroid.**

MARKDOWN


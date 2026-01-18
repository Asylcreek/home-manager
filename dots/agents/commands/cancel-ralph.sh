#!/bin/bash

# Cancel Ralph Loop - Executable version

STATE_FILE=".factory/ralph-loop.local.md"

if [ ! -f "$STATE_FILE" ]; then
    echo "No active Ralph loop found."
    echo "The /cancel-ralph command has completed. No further action needed."
    exit 0
fi

# Get current iteration
ITERATION=$(grep '^iteration:' "$STATE_FILE" | sed 's/iteration: *//')

# Remove state file
rm "$STATE_FILE"

echo "Cancelled Ralph loop (was at iteration $ITERATION)"
echo "The loop has been stopped and will not continue."
echo "No further action is required."

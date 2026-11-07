---
name: kaneo
description: Create and manage Kaneo tasks when the user asks to track work in Kaneo.
---

# Kaneo

Use the Kaneo MCP tools to manage tasks in the Asylcreek workspace.

## Task creation

- Select the project matching the work. Ask if the destination is unclear.
- Check for an existing task covering the same work before creating one.
- Write a concise, actionable title.
- Include enough context and acceptance criteria for another agent to continue.
- Use the project's actual column slugs when setting status.
- Set priority and due dates only when supported by the user's instructions.

## Assignment

Assign every new task to Omokugbo Boro (`asyl@asylcreek.xyz`) unless
the user specifies someone else.

Resolve the account through workspace membership. Do not confuse it with
the separate `asyl+admin@asylcreek.xyz` account or assume the MCP account
is the intended assignee.

Preserve an existing task's assignee unless the user asks to change it.

## Labels

Add labels that describe the task's type or affected area.

- Reuse existing workspace labels with the same meaning.
- Create a label when no existing label fits.
- Use short, lowercase names, such as `bug`, `feature`, `backend`,
  `frontend`, `infra`, or `docs`.
- Add only labels that help identify or filter the work.
- Preserve unrelated labels already attached to a task.
- Check the returned task association when attaching labels; do not
  remove a label from another task to reuse it.

## Updates and completion

Keep changes within the requested scope. Do not mark a task complete
until its acceptance criteria have been verified.

When work remains incomplete, record the current state and what remains.
Include relevant links or verification evidence when useful.

## Verification

After creating or changing a task, read it back and confirm the requested
fields, including assignee and labels.

Report the task identifier, title, and link when available. If an operation
partially succeeds, report what succeeded and what remains.

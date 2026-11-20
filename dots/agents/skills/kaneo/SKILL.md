---
name: kaneo
description: Read, create, and manage Kaneo tasks, including opening images in task descriptions and comments.
---

# Kaneo

Use the Kaneo MCP tools to manage tasks in the Asylcreek workspace.

## Task images

When reading a task, automatically download and open any Kaneo-hosted
images in its description and in comments you read. The MCP tools return
image links as text. Fetch the image with the existing `KANEO_API_KEY`
in the `x-api-key` header, save it to a private temporary file, and open
it with your local image viewer or image tool.

Send the key only to `https://kaneo.asylcreek.xyz/api/asset/<id>`. Resolve
relative asset URLs against that origin. Keep the key out of command
arguments and logs, and do not follow redirects with the key.

```sh
printf 'header = "x-api-key: %s"\n' "$KANEO_API_KEY" |
  curl --config - --fail --silent --show-error --max-time 30 \
    --output "$image_file" "$asset_url"
```

If the key is unavailable or the download fails, report which image you
could not open.

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

## Memory

When creating a task as done, link the relevant memory note under "Memory"
in its description. Retrieve the URL through the memory workflow and use
the note title as link text.

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

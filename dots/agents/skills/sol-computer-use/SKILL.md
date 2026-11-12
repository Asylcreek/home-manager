---
name: sol-computer-use
description: Use when a task needs clicking, typing, or screenshots in a desktop app. Not for web pages (use preview_* or agent-browser) or iOS/Android simulators (use device_*).
---

Claude has no native computer use here. Codex does. Hand the GUI work
to Codex; you own the goal, the safety limits, and checking the result.

## Defaults

- Model: GPT-6.1 Sol. Reasoning: Low. Regular speed.
- One Codex task per GUI job. Codex must not hand the task to another agent.
- Do not switch models or raise effort silently.

## Before handing off

1. Confirm the task really needs desktop control. If preview__,
   device__, agent-browser, or a shell command can do it, use that.
2. Write a self-contained brief:
   - Goal and target app.
   - Starting state and what counts as done.
   - What Codex may touch, and what it must not touch.
   - What to return.

## T3 Code route

- Call orchestrator_capabilities and find gpt-6.1-sol under Codex.
- Call delegate_task with target codex / gpt-6.1-sol, reasoningEffort
  low. Use mode "wait" for short jobs and "async" for long ones.
- If the model isn't available, report it. Do not substitute another one.

## Terminal fallback

    codex exec --model gpt-6.1-sol -c model_reasoning_effort=low -

Pass the brief through stdin. Do not change global Codex config or auth.

## Safety

Without explicit user approval stated in the brief, Codex must not:

- purchase anything, or send messages or email
- delete files or data
- change system settings, permissions, or accounts
- enter credentials

If one of these comes up, Codex stops and reports back.

## Instructions to include in every brief

Use computer use to do only the task below. Do not delegate.
Take a screenshot at the end, plus one at any failure.
Return:

- DONE, BLOCKED, or PARTIAL
- the steps you took
- what you observed on screen
- the saved screenshot paths
  Separate what you saw from what you assume.

## After

- Look at the returned screenshots yourself before claiming success.
- Report what is confirmed (with screenshot paths), what Codex claims
  but is unverified, and what is blocked.

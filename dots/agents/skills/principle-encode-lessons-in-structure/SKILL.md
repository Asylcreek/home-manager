---
name: principle-encode-lessons-in-structure
description: "Apply when you catch yourself writing the same instruction a second time, or notice a recurring correction. Encode the rule as a lint, metadata flag, runtime check, or script instead of more text."
disable-model-invocation: true
---

# Encode Lessons in Structure

Encode recurring fixes in mechanisms (tools, code, metadata, automation) instead of textual instructions. Every error, human correction, and unexpected outcome is a learning signal. Capture it, route it, and close the loop.

**Why:** Textual instructions are easy to miss. They require the reader to notice, remember, and comply. Structural mechanisms (lint rules, metadata flags, runtime checks, automation scripts) enforce the rule without cooperation.

**Pattern:**
When you catch yourself writing the same instruction a second time:
1. Ask: can this be a lint rule, a metadata flag, a runtime check, or a script?
2. Confirm the pattern is recurring, the structural mechanism belongs to the current scope, and the user has authorized that change.
3. If yes, encode it and remove redundant instructions.
4. If not, recommend the structural follow-up without expanding the current task.

**Pick the strongest rung.** When more than one mechanism would work, choose the strongest the situation allows (an unrepresentable state that cannot compile, then a lint or banned API that fails CI, then a canonical helper, then a runtime check), because agents copy whatever the surrounding code already does and a weaker guard becomes the next template.

**Corollary:** Do not paper over a confirmed structural cause with another instruction. A local symptom fix may still be appropriate when the broader mechanism is unproven, out of scope, or not authorized.

**Feedback loop:**
- **Assess corrections.** When the human intervenes or tests fail, decide whether the evidence shows a one-off or a recurring pattern.
- **Route to the owned layer.** Prefer a local code or tooling mechanism over new global instructions. Never edit skills, memory, or user-wide configuration unless the user explicitly asks.
- **Close the loop within scope.** Apply an authorized mechanism now or report one concrete follow-up.

**Anti-patterns:**
- Acknowledging without recording ("I'll keep that in mind" does not persist)
- Recording without routing (a brain note about a lint rule that should exist is wasted unless the lint rule gets implemented)
- Fixing without generalizing (fixing one instance while leaving the recurring pattern intact)

---
name: typescript-best-practices
description: Apply TypeScript-specific type safety and API-design practices when materially designing, editing, or reviewing TypeScript. Do not use for trivial reads, generated code, or tasks where TypeScript syntax is incidental.
---

# TypeScript best practices

Use these practices proportionally. Match the repository's established conventions unless changing them is part of the task.

| Rule | Summary |
|------|---------|
| Discriminated unions | Model variants with a `kind` literal discriminant so impossible states can't be represented. No optional-field bags. |
| Branded types | Brand same-shaped values only when accidental interchange is a real risk. Validate at the owning boundary. |
| Constructive modeling | Build the shape so the illegal value can't be constructed. `[T, ...T[]]` for non-empty, `[T, T][]` for even length, `start` plus `duration` for a range. Not a runtime guard, not a wish for refinement types. |
| Simplest total type | Keep `T[]` while every operation on it stays total. Strengthen to `NonEmpty<T>` only where the loose type forces `!`, a cast, or a "should never happen" throw. |
| `unknown` over `any` | External data is `unknown`. `any` disables type checking everywhere it touches. |
| Prefer inference | Let TypeScript infer local variable and function return types when the inferred type is clear and correct. Annotate when the type defines a public contract, prevents unintended widening, supports recursion or overloads, or materially improves readability or diagnostics. |
| Minimize `as` casts | Prefer narrowing or validation. Keep unavoidable framework or boundary casts local and evidenced. |
| Narrowing hierarchy | Discriminant switch > `in` operator > `typeof`/`instanceof` > user-defined type guard > `as`. |
| Type guards | Must verify the claim. A lying guard is worse than `as` because the bug hides behind a name that says it's safe. Name them `isX` or `hasX`. |
| Exhaustiveness | Inline `const _exhaustive: never = x;` in default arms so the compiler errors when a new variant is added. |
| `satisfies` over `as` | Validates the value without widening literal types. |
| Boundary validation | Validate external data where it crosses into the owned model; trust types inside. |
| Schema-derived types | Reach for `Pick`/`Omit`/`Parameters`/`ReturnType`/`Awaited`/`typeof` before declaring a new interface. |
| Object args | Prefer an object when several parameters are optional, same-shaped, or easy to swap. Keep short conventional signatures simple. |

Examples: `references/patterns.md`.

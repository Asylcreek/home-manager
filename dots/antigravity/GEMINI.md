## MCP Fallback (Antigravity ACP)

If the `basic-memory` or `kaneo` MCP tools are not loaded in this session (for example, when running under T3 Code's isolated `GEMINI_HOME`), delegate `remember`, `recall`, and `kaneo` operations to the standalone `agy` CLI inside an interactive shell so `KANEO_API_KEY` is loaded (without it, `@kaneo/mcp` falls back to device OAuth):

```sh
zsh -ic 'agy --dangerously-skip-permissions -p "$1"' _ "$prompt"
```

Place `--dangerously-skip-permissions` before `-p`. Only report that a memory or Kaneo operation failed if both direct MCP tools and this fallback fail.

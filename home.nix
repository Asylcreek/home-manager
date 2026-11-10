{config, lib, ...}: let
  dotfiles = "${config.home.homeDirectory}/.config/home-manager/dots";
  link = path: config.lib.file.mkOutOfStoreSymlink "${dotfiles}/${path}";
in {
  imports = [./shell];

  home.username = "asyl";
  home.homeDirectory = "/home/asyl";
  home.stateVersion = "24.05";

  # Omarchy installs applications. Home Manager only installs its own CLI.
  programs.home-manager.enable = true;
  xdg.enable = true;
  xdg.mime.enable = false;
  programs.man.enable = false;
  manual.manpages.enable = false;

  xdg.configFile = {
    "mise/config.toml".source = link "mise/config.toml";
    "lazygit/config.yml".source = link "lazygit/config.yml";
    "opencode/opencode.jsonc".source = link "opencode/opencode.jsonc";
    "oh-my-posh".source = link "oh-my-posh";
  };

  home.file = lib.mkMerge ([
    {
      ".claude/settings.json".source = link "claude/settings.json";
      ".claude/statusline-command.sh".source = link "claude/statusline-command.sh";
      ".codex/config.toml".source = link "codex/config.toml";
      ".codex/agents".source = link "agents/codex-named-agents";
      ".factory/scripts".source = link "agents/scripts";
    }
  ] ++ map (target: {
    "${target}/${if lib.hasPrefix ".claude" target then "CLAUDE.md" else "AGENTS.md"}".source = link "agents/AGENTS.md";
    "${target}/${if target == ".factory" then "droids" else if target == ".codex" then "sagents" else "agents"}".source = link "agents/agents";
    "${target}/commands".source = link "agents/commands";
    "${target}/docs-rules".source = link "agents/docs-rules";
    "${target}/skills".source = link "agents/skills";
  }) [".factory" ".agents" ".claude" ".claude-minimax" ".claude-kimi" ".claude-cliproxy" ".codex"]);

  # Claude keeps MCP servers with mutable account and session state in ~/.claude.json.
  home.activation.configureClaudeMcp = lib.hm.dag.entryAfter ["linkGeneration"] ''
    run /usr/bin/python3 - <<'PY'
    import json
    import os
    import tempfile
    from pathlib import Path

    target = Path.home() / ".claude.json"
    source = Path.home() / ".config/home-manager/dots/claude/mcp.json"
    original = target.read_text() if target.exists() else None
    config = json.loads(original) if original is not None else {}
    managed = json.loads(source.read_text())["mcpServers"]
    servers = {**config.get("mcpServers", {}), **managed}
    if config.get("mcpServers") != servers:
        config["mcpServers"] = servers
        with tempfile.NamedTemporaryFile(mode="w", dir=target.parent, prefix=".claude-mcp-", delete=False) as temporary:
            json.dump(config, temporary, indent=2)
            temporary.write("\n")
        if (target.read_text() if target.exists() else None) != original:
            os.unlink(temporary.name)
            raise RuntimeError("Claude configuration changed during activation; retry")
        os.replace(temporary.name, target)
    PY
  '';
}

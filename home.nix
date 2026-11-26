{
  lib,
  pkgs,
  ...
}: {
  imports = [
    ./shell
    ./services/t3code.nix
  ];

  home.username = "coder";
  home.homeDirectory = "/home/coder";

  home.stateVersion = "24.05";

  home.packages = with pkgs; [
    carapace
    lazygit
    tmux
    tmuxPlugins.resurrect
    tmuxPlugins.continuum
    fd
    ripgrep
    diff-so-fancy
  ];

  home.sessionVariables = {
    EDITOR = "nvim";
  };

  home.sessionPath = [
    "$HOME/.nix-profile/bin"
    "$HOME/.local/share/mise/shims"
    "$HOME/.local/bin"
  ];

  programs.home-manager.enable = true;

  xdg.enable = true;

  xdg.configFile = {
    "lazygit/config.yml".source = ./dots/lazygit/config.yml;
    "oh-my-posh".source = ./dots/oh-my-posh;

    "tmux/tmux.conf".source = ./dots/tmux/tmux.conf;
  };

  home.activation.linkAgents = lib.hm.dag.entryAfter ["linkGeneration"] ''
    agentSource="$HOME/.config/home-manager/dots/agents"

    declare -A nameMap=(
      [.agents]="AGENTS.md"
      [.claude]="CLAUDE.md"
      [.codex]="AGENTS.md"
    )

    declare -A agentsMap=(
      [.agents]="agents"
      [.claude]="agents"
      [.codex]="sagents"
    )

    for target in .agents .claude .codex; do
      mkdir -p $HOME/$target
      ln -sfn $agentSource/AGENTS.md $HOME/$target/''${nameMap[$target]}
      ln -sfn $agentSource/agents $HOME/$target/''${agentsMap[$target]}
      ln -sfn $agentSource/commands $HOME/$target
      ln -sfn $agentSource/docs-rules $HOME/$target
      ln -sfn $agentSource/skills $HOME/$target
    done

    mkdir -p "$HOME/.gemini/antigravity-cli" "$HOME/.gemini/config"
    mkdir -p "$HOME/.config/mise"

    ln -sfn "$agentSource/codex-named-agents" "$HOME/.codex/agents"
    ln -sfn "$HOME/.config/home-manager/dots/codex/config.toml" "$HOME/.codex/config.toml"

    ln -sfn "$HOME/.config/home-manager/dots/claude/settings.json" "$HOME/.claude/settings.json"
    ln -sfn "$HOME/.config/home-manager/dots/claude/statusline-command.sh" "$HOME/.claude/statusline-command.sh"

    ln -sfn "$agentSource/skills" "$HOME/.gemini/config/skills"
    ln -sfn "$HOME/.config/home-manager/dots/antigravity/GEMINI.md" "$HOME/.gemini/GEMINI.md"
    ln -sfn "$HOME/.config/home-manager/dots/antigravity/settings.json" "$HOME/.gemini/antigravity-cli/settings.json"
    ln -sfn "$HOME/.config/home-manager/dots/antigravity/mcp_config.json" "$HOME/.gemini/config/mcp_config.json"

    ln -sfn "$HOME/.config/home-manager/dots/mise/config.toml" "$HOME/.config/mise/config.toml"
  '';
  # Claude keeps MCP servers with mutable account and session state in ~/.claude.json.
  home.activation.configureClaudeMcp = lib.hm.dag.entryAfter ["writeBoundary"] ''
    run ${pkgs.python3}/bin/python3 - <<'PY'
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

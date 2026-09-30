{
  lib,
  pkgs,
  ...
}: {
  imports = [
    ./shell
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
      [.factory]="AGENTS.md"
      [.agents]="AGENTS.md"
      [.claude]="CLAUDE.md"
      [.claude-minimax]="CLAUDE.md"
      [.claude-kimi]="CLAUDE.md"
      [.claude-cliproxy]="CLAUDE.md"
      [.codex]="AGENTS.md"
    )

    declare -A agentsMap=(
      [.factory]="droids"
      [.agents]="agents"
      [.claude]="agents"
      [.claude-minimax]="agents"
      [.claude-kimi]="agents"
      [.claude-cliproxy]="agents"
      [.codex]="sagents"
    )

    for target in .factory .agents .claude .claude-minimax .claude-kimi .claude-cliproxy .codex; do
      mkdir -p $HOME/$target
      ln -sfn $agentSource/AGENTS.md $HOME/$target/''${nameMap[$target]}
      ln -sfn $agentSource/agents $HOME/$target/''${agentsMap[$target]}
      ln -sfn $agentSource/commands $HOME/$target
      ln -sfn $agentSource/docs-rules $HOME/$target
      ln -sfn $agentSource/skills $HOME/$target
    done

    mkdir -p "$HOME/.config/mise"
    ln -sfn "$HOME/.config/home-manager/dots/mise/config.toml" "$HOME/.config/mise/config.toml"
    ln -sfn "$agentSource/scripts" "$HOME/.factory/scripts"
    ln -sfn "$agentSource/codex-named-agents" "$HOME/.codex/agents"
  '';
}

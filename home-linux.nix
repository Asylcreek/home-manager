{config, lib, pkgs, ...}: {
  imports = [./shell];

  home.username = "coder";
  home.homeDirectory = "/home/coder";
  home.stateVersion = "24.05";
  home.packages = with pkgs; [carapace lazygit tmux fd ripgrep diff-so-fancy];
  home.sessionPath = ["$HOME/.nix-profile/bin" "$HOME/.local/share/mise/shims" "$HOME/.local/bin"];
  home.sessionVariables.EDITOR = "nvim";
  programs.home-manager.enable = true;
  xdg.enable = true;

  xdg.configFile = {
    "lazygit/config.yml".source = ./dots/lazygit/config.yml;
    "oh-my-posh".source = ./dots/oh-my-posh;
    "tmux/tmux.conf".text = lib.replaceStrings
      ["/Users/asyl/.nix-profile/bin/zsh" "run '$HOMEBREW_PREFIX/opt/tpm/share/tpm/tpm'" "run-shell -b '$HOME/.ibudo/integrations/ibudo-tmux/ibudo.tmux'"]
      ["${pkgs.zsh}/bin/zsh" "run '${pkgs.tmuxPlugins.resurrect}/share/tmux-plugins/resurrect/resurrect.tmux'\nrun '${pkgs.tmuxPlugins.continuum}/share/tmux-plugins/continuum/continuum.tmux'" "if-shell 'test -f $HOME/.ibudo/integrations/ibudo-tmux/ibudo.tmux' 'run-shell -b $HOME/.ibudo/integrations/ibudo-tmux/ibudo.tmux'"]
      (builtins.readFile ./dots/tmux/tmux.conf);
  };

  home.file = let
    targets = [".agents" ".codex" ".factory" ".claude"];
    links = lib.concatMap (target: [
      {name = "${target}/skills"; value.source = ./dots/agents/skills;}
      {name = "${target}/commands"; value.source = ./dots/agents/commands;}
      {name = "${target}/docs-rules"; value.source = ./dots/agents/docs-rules;}
      {name = "${target}/agents"; value.source = ./dots/agents/agents;}
    ]) targets;
  in builtins.listToAttrs links // {
    ".claude/CLAUDE.md".source = ./dots/claude/CLAUDE.md;
    ".agents/AGENTS.md".source = ./dots/agents/AGENTS.md;
    ".codex/AGENTS.md".source = ./dots/agents/AGENTS.md;
    ".factory/AGENTS.md".source = ./dots/agents/AGENTS.md;
  };
}

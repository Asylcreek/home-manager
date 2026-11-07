{pkgs, ...}: {
  imports = [./shell];

  home.username = "root";
  home.homeDirectory = "/root";
  home.stateVersion = "24.05";

  home.packages = with pkgs; [
    neovim
    # nvim-treesitter compiles parsers using these tools.
    stdenv.cc
    tree-sitter
    tmux
    tmuxPlugins.resurrect
    tmuxPlugins.continuum
    fd
    ripgrep
  ];

  home.sessionVariables.EDITOR = "nvim";
  # System Zsh must find Nix tools without relying on Bash's startup hooks.
  home.sessionPath = [
    "$HOME/.nix-profile/bin"
    "/nix/var/nix/profiles/default/bin"
  ];

  programs.home-manager.enable = true;
  xdg.enable = true;
  xdg.configFile."tmux/tmux.conf".source = ./dots/tmux/tmux.conf;
}

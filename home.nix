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

  programs.home-manager.enable = true;
  xdg.enable = true;
  xdg.configFile."tmux/tmux.conf".source = ./dots/tmux/tmux.conf;
}

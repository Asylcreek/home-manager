{...}: {
  programs.tmux = {
    enable = true;
    package = null;
    sensibleOnTop = false;
    shell = "/usr/bin/zsh";
    extraConfig = builtins.readFile ../../dots/tmux/tmux.conf;
  };
}

{
  config,
  lib,
  pkgs,
  ...
}: let
  ompConfigPath = pkgs.writeText "kali.omp.json" (builtins.readFile ../../dots/oh-my-posh/kali.omp.json);
in {
  home.packages = [pkgs.oh-my-posh];

  programs.zsh = {
    enable = true;
    dotDir = config.home.homeDirectory;
    autosuggestion.enable = true;
    enableCompletion = false;

    oh-my-zsh = {
      enable = true;
      plugins = ["git"];
      theme = "";
    };

    plugins = [
      {
        name = "zsh-autocomplete";
        src = pkgs.zsh-autocomplete;
        file = "share/zsh-autocomplete/zsh-autocomplete.plugin.zsh";
      }
    ];

    shellAliases = {
      "v" = "nvim";
      "ta" = "tmux a -t ";
      "hsf" = "home-manager switch --flake path:$HOME/.config/home-manager#proxmox";
    };

    syntaxHighlighting.enable = true;

    history = {
      expireDuplicatesFirst = true;
      ignoreAllDups = true;
      extended = true;
    };

    initContent = lib.mkMerge [
      (lib.mkBefore ''
        zstyle ':autocomplete:*' delay 0.1
        zstyle ':autocomplete:*' timeout 1.5
        zstyle ':autocomplete:*' min-input 2
        zstyle -e ':autocomplete:*:*' list-lines 'reply=( 12 )'
        zstyle ':autocomplete:*' add-semicolon no
      '')
      ''
        eval "$(oh-my-posh init zsh --config ${ompConfigPath})"

        if [ -n "$GHOSTTY_RESOURCES_DIR" ]; then
          builtin source "$GHOSTTY_RESOURCES_DIR/shell-integration/zsh/ghostty-integration"
        fi

        bindkey '\ez' clear-screen

        [ -r "$HOME/.ibudo/shell-integration/ibudo.zsh" ] &&
          . "$HOME/.ibudo/shell-integration/ibudo.zsh"
      ''
      (lib.mkAfter ''
        bindkey -M menuselect '\r' .accept-line
      '')
    ];
  };
}

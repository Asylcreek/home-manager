{ pkgs, ... }:

let
  precmdScriptPath = pkgs.writeText "precmd.zsh" (builtins.readFile ./precmd.zsh);
in

{
  home.packages = with pkgs; [
    oh-my-posh
  ];

  programs.zsh = {
    enable = true;

    autosuggestion = {
      enable = true;
    };

    enableCompletion = true;

    oh-my-zsh = {
      enable = true;
      plugins = [ "git" ];
      theme = "";
    };

    shellAliases = {
      "dv" = "cd ~/Downloads/Video";
      "vlc" = "/Applications/VLC.app/Contents/MacOS/VLC";
      "v" = "nvim";
      "python" = "python3";
      "ta" = "tmux a -t ";
      "dash" = "ta gh && tmux send-keys -t 0 'gh dash' Enter";
      "dots" = "/usr/bin/git --git-dir=$HOME/.dots/ --work-tree=$HOME";
      "edng" = "v ~/Library/Application\\ Support/ngrok/ngrok.yml";
      "hsf" = "darwin-rebuild switch --impure";
      "dr" = "doppler run -- ";
      "psd" = "pnpm start:dev";
      "pd" = "pnpm dev";
      "pb" = "pnpm build";
      "pi" = "pnpm install";
      "pa" = "pnpm add";
      "yb" = "yarn build";
      "yd" = "yarn dev";
      "ysd" = "yarn start:dev";
      "uc" = "brew outdated && brew upgrade && brew upgrade --cask --greedy && brew cleanup";
      "p8" = "ns -p pnpm_8";
      "k" = "sudo kanata --cfg ~/.config/kanata/config.kbd";
    };

    syntaxHighlighting = {
      enable = true;
    };

    history = {
      expireDuplicatesFirst = true;
      ignorePatterns = [ "doppler*" ];
      ignoreAllDups = true;
      extended = true;
    };

    initExtra = ''
      ns() {
        export context_display="$*" 

        nix-shell "$@" --run '
          export NIX_CONTEXT_DISPLAY="$context_display";
          zsh
        '
      }

      # possible options: emodipt-extend, kali, pure, negligible, craver, honukai, wopian
      eval "$(oh-my-posh init zsh --config $HOME/.nix-profile/share/oh-my-posh/themes/negligible.omp.json)"

      source "${precmdScriptPath}"

      # fnm
      eval "$(fnm env --use-on-cd --resolve-engines)" 

      # Amazon Q post block. Keep at the bottom of this file.
      [[ -f "$HOME/Library/Application Support/kiro-cli/shell/zshrc.post.zsh" ]] && builtin source "$HOME/Library/Application Support/kiro-cli/shell/zshrc.post.zsh"
    '';

    initExtraFirst = ''
      # Amazon Q pre block. Keep at the top of this file.
      [[ -f "$HOME/Library/Application Support/kiro-cli/shell/zshrc.pre.zsh" ]] && builtin source "$HOME/Library/Application Support/kiro-cli/shell/zshrc.pre.zsh"
      '';
  };
}

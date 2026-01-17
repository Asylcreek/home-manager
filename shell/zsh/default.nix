{ pkgs, ... }:

let
  ompConfigPath = pkgs.writeText "negligible.omp.json" (builtins.readFile ../../dots/oh-my-posh/negligible.omp.json);
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
      # load .env
      if [ -f $HOME/.env ]; then
        export $(cat $HOME/.env | xargs)
      fi

      ns() {
        export context_display="$*"

        nix-shell "$@" --run '
          export NIX_CONTEXT_DISPLAY="$context_display";
          zsh
        '
      }

      # Custom Oh My Posh config with nix-shell segment
      eval "$(oh-my-posh init zsh --config ${ompConfigPath})"

      # Function to set context for Oh My Posh before each prompt
      # Define this AFTER oh-my-posh init to avoid being overwritten
      function set_poshcontext() {
        # Populate NIX_CONTEXT_DISPLAY if we're in a nix-shell
        if [[ -n "$IN_NIX_SHELL" && -n "$NIX_CONTEXT_DISPLAY" ]]; then
          export POSH_NIX_CONTEXT="$NIX_CONTEXT_DISPLAY"
        else
          unset POSH_NIX_CONTEXT
        fi
      }

      # Register the hook to run before every prompt
      autoload -U add-zsh-hook
      add-zsh-hook precmd set_poshcontext


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

  programs.direnv ={
    enable = true;
    nix-direnv = {
      enable = true;
    };
  };
}
